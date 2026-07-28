---
name: azure-devops-build-logs
description: Buscar timeline e logs de builds do Azure DevOps usando Azure CLI e o fallback confiavel `az devops invoke --area build --resource logs`. Use quando o usuario informar `buildId`, `logId`, `definitionId`, pedir ultimo log de execucao de uma pipeline, pedir logs completos de uma task, ou quando `az pipelines build logs` nao existir no ambiente local.
---

# Azure DevOps Build Logs

## Objetivo

Coletar logs de build do Azure DevOps sem precisar redescobrir a sintaxe do endpoint Build Logs API.

Contexto padrao deste repositorio:

- Organization: `https://dev.azure.com/oec-eng`
- Project: `terraform-gcp-infra`
- CLI: `az` com extensao `azure-devops`
- Reautenticacao local, quando necessario: `./reautenticar.sh`

## Regra Operacional

Use somente comandos read-only:

- `az pipelines build show`
- `az pipelines build list`
- `az devops invoke --area build --resource timeline`
- `az devops invoke --area build --resource logs`

Nao executar comandos que criem, alterem, cancelem ou removam builds, recursos cloud ou configuracoes.

## Fluxo Recomendado

1. Se o usuario informar `buildId`, use esse build diretamente.
2. Se o usuario informar `definitionId`, descubra o build mais recente dessa pipeline:
   ```bash
   az pipelines build list --definition-ids <DEFINITION_ID> --top 1 \
     --org https://dev.azure.com/oec-eng \
     --project terraform-gcp-infra
   ```
3. Baixe o resumo do build com `az pipelines build show`.
4. Baixe a timeline do build com:
   ```bash
   az devops invoke \
     --area build \
     --resource timeline \
     --route-parameters project=terraform-gcp-infra buildId=<BUILD_ID> \
     --org https://dev.azure.com/oec-eng \
     --api-version 7.1 \
     -o json
   ```
5. Escolha o `logId`:
   - se o usuario informou `logId`, use esse valor;
   - se pediu ultimo log, escolha o maior `log.id` presente na timeline;
   - se precisa diagnosticar falha, prefira a task com `result=failed`; se nao houver, use a ultima task com log.
6. Baixe o log com o comando canonico:
   ```bash
   az devops invoke \
     --area build \
     --resource logs \
     --route-parameters project=terraform-gcp-infra buildId=<BUILD_ID> logId=<LOG_ID> \
     --org https://dev.azure.com/oec-eng \
     --api-version 7.1 \
     -o json
   ```
7. Extraia `.value[]` do JSON para texto quando a resposta vier como array de linhas.

## Script

Use o script do skill para automatizar o fluxo:

```bash
.agents/skills/azure-devops-build-logs/scripts/fetch_build_logs.sh --build-id 1271 --log-id 25
```

Buscar automaticamente o ultimo log da ultima execucao de uma pipeline:

```bash
.agents/skills/azure-devops-build-logs/scripts/fetch_build_logs.sh --definition-id 2 --latest-log
```

Buscar todos os logs de uma execucao:

```bash
.agents/skills/azure-devops-build-logs/scripts/fetch_build_logs.sh --build-id 1271 --all-logs
```

Para exibir um preview no terminal, use explicitamente:

```bash
.agents/skills/azure-devops-build-logs/scripts/fetch_build_logs.sh --build-id 1271 --log-id 25 --tail 40
```

Por padrao, o script nao imprime conteudo do log no terminal para reduzir risco de exposicao de segredos, emails, IDs internos ou outputs sensiveis do Terraform.

Saida padrao:

- `/tmp/azure-devops-build-logs/build-<BUILD_ID>-summary.json`
- `/tmp/azure-devops-build-logs/build-<BUILD_ID>-timeline.json`
- `/tmp/azure-devops-build-logs/build-<BUILD_ID>-timeline.tsv`
- `/tmp/azure-devops-build-logs/build-<BUILD_ID>-log-<LOG_ID>.json`
- `/tmp/azure-devops-build-logs/build-<BUILD_ID>-log-<LOG_ID>.log`

## Diagnostico

Se o Azure CLI falhar por autenticacao:

```bash
./reautenticar.sh
```

Se `az pipelines` nao reconhecer argumentos de DevOps:

```bash
az extension add --name azure-devops --upgrade
```

Se `az pipelines build logs` nao existir, nao insistir nesse comando. Use `az devops invoke --area build --resource logs`, que e o fallback oficial deste skill.

## Resposta Ao Usuario

Ao final, informe:

1. build analisado;
2. pipeline/definition quando disponivel;
3. `status` e `result`;
4. `logId` coletado;
5. caminho do `.log` em texto puro;
6. ultimas linhas relevantes ou erro principal apenas quando necessario, sanitizando dados sensiveis e sem despejar log completo no chat.
