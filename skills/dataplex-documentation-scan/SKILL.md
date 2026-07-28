---
name: dataplex-documentation-scan
description: Guia e automação para criar, disparar e publicar scans de documentação de dados (Data Documentation) do Dataplex em tabelas do BigQuery, incluindo o ciclo completo de monitoramento e vinculação por labels.
---

# Dataplex Data Documentation Scan

Este guia instrui o assistente sobre como gerenciar o ciclo de vida de um scan de documentação de dados (**Data Documentation**) do Google Cloud Dataplex (Knowledge Catalog) para tabelas do BigQuery.

O ciclo de vida do processo é composto por 4 fases:
1. **Criação do recurso Data Scan** no Dataplex (tipo `DATA_DOCUMENTATION`).
2. **Disparo do Job de Scan** no Dataplex.
3. **Monitoramento do status** do Job até que mude para `SUCCEEDED`.
4. **Publicação dos resultados na tabela** aplicando os labels de relacionamento do BigQuery.

---

## 🛠️ Pré-requisitos

* O ambiente de terminal local deve estar autenticado com um perfil gcloud válido (administrativo `cld-rheron` ou corporativo `rheron`).
* Certifique-se de que a API do Dataplex (`dataplex.googleapis.com`) esteja ativa no projeto de destino.

---

## 🚀 Fluxo de Trabalho e Comandos

### 1. Criação do Scan no Dataplex (Standard Managed)

O scan deve ser criado na região correspondente ao dataset. Substitua as variáveis no comando `curl` abaixo:

```bash
ACCESS_TOKEN=$(gcloud auth print-access-token)

curl -X POST \
  "https://dataplex.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION}/dataScans?dataScanId=${DATASCAN_ID}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "resource": "//bigquery.googleapis.com/projects/'"${PROJECT_ID}"'/datasets/'"${DATASET_ID}"'/tables/'"${TABLE_ID}"'"
    },
    "executionSpec": {
      "trigger": { "onDemand": {} }
    },
    "type": "DATA_DOCUMENTATION",
    "dataDocumentationSpec": {
      "generationScopes": "ALL",
      "catalogPublishingEnabled": true
    }
  }'
```

* **PROJECT_ID**: ID do projeto GCP (ex: `prj-incorta-oecx8`).
* **LOCATION**: Região do scan e do dataset (ex: `us-east1` ou `us-central1`).
* **DATASET_ID**: ID do dataset (ex: `EBS_PO`).
* **TABLE_ID**: Nome da tabela (ex: `APPS_ORG_ORGANIZATION_DEFINITIONS_2025`).
* **DATASCAN_ID**: ID do scan único (sugestão: `ds-${DATASET_ID}-${TABLE_ID}` formatado em minúsculas e usando hifens, ex: `ds-ebs-po-apps-org-organization-definitions-2025`).

### 2. Disparo da Execução do Scan

Com o scan criado, dispare a execução:

```bash
ACCESS_TOKEN=$(gcloud auth print-access-token)

curl -X POST \
  "https://dataplex.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION}/dataScans/${DATASCAN_ID}:run" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

O retorno deste comando fornecerá um **Job ID** no campo `name` (formato `projects/.../jobs/JOB_ID`).

### 3. Monitoramento do Status

Consulte periodicamente o status do Job até que mude para `SUCCEEDED` ou `FAILED`:

```bash
ACCESS_TOKEN=$(gcloud auth print-access-token)

curl -s -X GET \
  "https://dataplex.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION}/dataScans/${DATASCAN_ID}/jobs/${JOB_ID}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" | grep -i state
```

### 4. Publicação dos Resultados (Labels no BigQuery)

Para que os insights gerados pelo Dataplex apareçam na aba **Insights** da respectiva tabela no BigQuery Console, é obrigatório aplicar os labels de mapeamento na tabela:

```bash
bq update \
  --set_label dataplex-data-documentation-published-scan:${DATASCAN_ID} \
  --set_label dataplex-data-documentation-published-project:${PROJECT_ID} \
  --set_label dataplex-data-documentation-published-location:${LOCATION} \
  ${PROJECT_ID}:${DATASET_ID}.${TABLE_ID}
```

---

## ⚡ Script de Execução Automatizada em Lote

Para rodar todo o fluxo acima de forma automatizada para uma ou mais tabelas, o seguinte script bash pode ser executado:

```bash
#!/bin/bash
set -e

# Configurações básicas
PROJECT_ID="prj-incorta-oecx8"
DATASET_ID="EBS_PO"
LOCATION="us-east1"

# Lista de tabelas a serem processadas
TABELAS=(
  "APPS_ORG_ORGANIZATION_DEFINITIONS_2025"
  "AP_AP_INVOICES_ALL_2025"
)

for TABLE_ID in "${TABELAS[@]}"; do
  # Formata o ID do DataScan (Dataplex exige minúsculas, números e hifens)
  DATASCAN_ID=$(echo "ds-${DATASET_ID}-${TABLE_ID}" | tr '_' '-' | tr '[:upper:]' '[:lower:]')
  
  echo "=============================================="
  echo "📦 Processando tabela: ${TABLE_ID}"
  echo "🎯 ID do DataScan: ${DATASCAN_ID}"
  echo "=============================================="

  ACCESS_TOKEN=$(gcloud auth print-access-token)

  # 1. Criar Scan no Dataplex (ignora erro se já existir)
  echo "1. Criando DataScan..."
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
    "https://dataplex.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION}/dataScans?dataScanId=${DATASCAN_ID}" \
    -H "Authorization: Bearer ${ACCESS_TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{
      "data": {
        "resource": "//bigquery.googleapis.com/projects/'"${PROJECT_ID}"'/datasets/'"${DATASET_ID}"'/tables/'"${TABLE_ID}"'"
      },
      "executionSpec": {
        "trigger": { "onDemand": {} }
      },
      "type": "DATA_DOCUMENTATION",
      "dataDocumentationSpec": {
        "generationScopes": "ALL",
        "catalogPublishingEnabled": true
      }
    }')

  if [ "$HTTP_CODE" == "200" ] || [ "$HTTP_CODE" == "201" ]; then
    echo "✅ DataScan criado com sucesso."
  elif [ "$HTTP_CODE" == "409" ]; then
    echo "⚠️ DataScan já existe. Prosseguindo..."
  else
    echo "❌ Erro ao criar DataScan (Status: $HTTP_CODE)."
    continue
  fi

  # 2. Executar o DataScan
  echo "2. Disparando execução do DataScan..."
  RUN_RESPONSE=$(curl -s -X POST \
    "https://dataplex.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION}/dataScans/${DATASCAN_ID}:run" \
    -H "Authorization: Bearer ${ACCESS_TOKEN}")
  
  JOB_ID=$(echo "$RUN_RESPONSE" | grep -o '"jobId": "[^"]*' | grep -o '[^"]*$')
  
  if [ -z "$JOB_ID" ]; then
    # Caso o jobId venha no formato completo da URI do recurso
    JOB_ID=$(echo "$RUN_RESPONSE" | grep -o '"name": "[^"]*' | grep -o '[^"]*$' | awk -F'/' '{print $NF}')
  fi

  if [ -z "$JOB_ID" ]; then
    echo "❌ Erro ao disparar o DataScan ou extrair o Job ID."
    echo "Resposta da API: $RUN_RESPONSE"
    continue
  fi

  echo "🚀 Job ID iniciado: $JOB_ID"

  # 3. Monitorar status
  echo "3. Aguardando conclusão do Job..."
  while true; do
    JOB_RESPONSE=$(curl -s -X GET \
      "https://dataplex.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION}/dataScans/${DATASCAN_ID}/jobs/${JOB_ID}" \
      -H "Authorization: Bearer ${ACCESS_TOKEN}")
    
    STATE=$(echo "$JOB_RESPONSE" | grep -o '"state": "[^"]*' | grep -o '[^"]*$')
    
    echo "   Estado atual: $STATE"
    
    if [ "$STATE" == "SUCCEEDED" ]; then
      echo "✅ Job concluído com sucesso!"
      break
    elif [ "$STATE" == "FAILED" ] || [ "$STATE" == "CANCELLED" ]; then
      echo "❌ Job falhou ou foi cancelado."
      break
    fi
    sleep 10
  done

  # 4. Vincular por Labels no BigQuery
  if [ "$STATE" == "SUCCEEDED" ]; then
    echo "4. Aplicando labels de publicação na tabela..."
    bq update \
      --set_label dataplex-data-documentation-published-scan:${DATASCAN_ID} \
      --set_label dataplex-data-documentation-published-project:${PROJECT_ID} \
      --set_label dataplex-data-documentation-published-location:${LOCATION} \
      ${PROJECT_ID}:${DATASET_ID}.${TABLE_ID}
    echo "🎉 Processo concluído para ${TABLE_ID}!"
  else
    echo "⚠️ Pulando aplicação de labels por falha no job."
  fi
  echo ""
done
```
