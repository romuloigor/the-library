---
name: codemender
description: "Executa auditorias e varreduras de segurança em repositórios usando o Google CodeMender CLI (cm) e Gemini Cyber (gemini-3.8-flash-cyber). Suporta modo baseline 100% offline (sem GCP) e auditoria semântica via Vertex AI. Obedece à governança estrita de isolamento em git worktree (sem commits ou merges diretos)."
metadata:
  preferred-model: "Gemini 3.8 Flash"
  preferred-model-id: "gemini-3.8-flash"
  profile-alias: "/codemender"
---

# 🛡️ Skill: Google CodeMender + Gemini Cyber

Esta skill orienta os agentes da Squad Antigravity na execução de auditorias e varreduras DevSecOps em qualquer repositório de código (Python, Java, TypeScript e Terraform).

---

## ⚡ 1. Diferença Crítica: Modo Offline vs Chamadas GCP (Vertex AI)

> [!IMPORTANT]
> **Atenção aos limites de conectividade, custos e ambiente:**
> * **`baseline` (100% OFFLINE / Sem GCP):**  
>   Executa inspeção estática determinística local. **Não faz chamadas de rede, não acessa o Google Cloud, não gera custos de API** e avalia o código localmente gerando matriz de evidências com hashes SHA-256 e contagem de linhas.
> * **`scan`, `scan-deep`, `scan-diff` (CHAMA O GCP):**  
>   Envia o código para o modelo **Gemini Cyber (`gemini-3.8-flash-cyber`)** no **Google Cloud Vertex AI** (projeto `prj-gemini-integration-oecx8`). **Requer autorização explícita do usuário antes de rodar caso haja restrição de chamadas ao GCP.**

---

## 🔍 2. Comandos Operacionais

### A. Repositórios com Wrapper Próprio (ex: `scripts/codemender-*.sh` ou `Makefile`)
Verifique se o repositório possui wrapper configurado:

```bash
# 1. Status e inventário de código
make codemender-status           # ou ./scripts/codemender-*.sh status

# 2. Varredura estática baseline local (100% OFFLINE, sem chamadas GCP)
make codemender-baseline         # ou ./scripts/codemender-*.sh baseline

# 3. Varredura semântica via Vertex AI (Requer GCP e autorização)
make codemender-scan             # ou ./scripts/codemender-*.sh scan

# 4. Varredura diferencial (somente alterações contra a main / PR via Vertex AI)
./scripts/codemender-*.sh scan-diff origin/main

# 5. Varredura estrita com bloqueio real em falhas (Fail-On Gate)
make codemender-strict           # ou ./scripts/codemender-*.sh baseline --strict
```

### B. Usando Diretamente o CLI Oficial (`cm`)
Caso queira invocar o binário `cm` diretamente:

```bash
# Varredura no diretório atual (Vertex AI)
cm find . --model gemini-3.8-flash-cyber

# Varredura profunda com raciocínio semântico contextual
cm find . --deep --model gemini-3.8-flash-cyber

# Varredura diferencial do branch atual contra origin/main
cm find . --diff origin/main --model gemini-3.8-flash-cyber

# Varredura de um arquivo específico
cm find path/to/file.ext --model gemini-3.8-flash-cyber
```

---

## 🛡️ 3. Nível de Rigor Operacional & Gate de Bloqueio (Fail-On)

O CodeMender suporta perfis de rigor estrito configurados via `scripts/codemender-config.yaml` ou flags de CLI:
* `rigor_level: "strict"`: Audita 12 regras OWASP Top 10 e CWE, incluindo:
  - **CWE-1236 (CSV/Formula Injection):** Injeção de fórmulas em exportação de relatórios.
  - **CWE-400 (Missing Timeout):** Subprocessos sem timeout explícito (risco de hang de daemons e runners).
  - **CWE-532 (Sensitive Logs):** Impressão de senhas/tokens em logs.
  - **Auditoria de Testes:** A pasta `tests/` é inspecionada para evitar credenciais hardcoded.
* `fail_on_severity: "MEDIUM"`: Se houver qualquer vulnerabilidade `MEDIUM`, `HIGH` ou `CRITICAL`, o processo retorna código de erro (`exit 1`), bloqueando pipelines e PRs.

---

## 📦 4. Binário `cm` e Variável `CM_INSTALL_DIR`

O binário `cm` é procurado no PATH ou no diretório especificado pela variável de ambiente `CM_INSTALL_DIR`:
* **Diretório padrão:** `CM_INSTALL_DIR="${HOME}/.local/bin"` (binário `${HOME}/.local/bin/cm`).
* **Instalação oficial:** Para instalar a partir do Google Artifact Registry corporativo (`cmoc-prod`):
  ```bash
  gcloud artifacts files download \
    --project=cmoc-prod \
    --location=us \
    --repository=codemender-cli-production \
    --package=cm \
    --version=stable \
    --destination=/tmp \
    cm-darwin-arm64.zip
  unzip -o /tmp/cm-darwin-arm64.zip -d "${CM_INSTALL_DIR}"
  chmod +x "${CM_INSTALL_DIR}/cm"
  ```
* **Fallback nativo:** Se o binário `cm` não estiver instalado, os repositórios da Squad utilizam runners Python nativos (`scripts/codemender_cyber_*_audit.py`) para interagir com a API do Vertex AI.

---

## 🔑 5. Diretiva Estrita de Autenticação

> [!CAUTION]
> **O agente NUNCA deve executar comandos interativos de login (ex: `gcloud auth application-default login`) por conta própria!**  
> Essa ação afeta credenciais globais da máquina do desenvolvedor. O agente deve apenas verificar se uma credencial já está ativa via:
> ```bash
> gcloud auth print-access-token
> ```
> Se não houver credencial ativa e o modo Vertex for necessário, o agente deve **solicitar que o usuário humano realize a autenticação**.

---

## 🔒 6. Governança Mandatória: Worktree Isolado, Sem Commit e Sem Merge Direto

> [!WARNING]
> **Comandos `cm verify` e `cm fix` executam código e geram alterações:**
> * `cm verify <VULN_ID>`: Reproduz a vulnerabilidade executando passos de compilação ou validação.
> * `cm fix <VULN_ID>`: Gera patches de remediação estruturada.
> 
> **Regras Obrigatórias da Squad Antigravity:**
> 1. **Isolamento em Git Worktree:** Toda reprodução (`verify`) e geração de patch (`fix`) DEVE ocorrer estritamente em um **git worktree temporário** (ex: `tmp/worktrees/...`).
> 2. **Proibição de Commit Direto:** O agente está **terminantemente proibido de fazer commit direto** desses patches no branch de trabalho principal (`main`).
> 3. **Proibição de Merge:** Nenhuma correção automática pode sofrer merge direto. Toda alteração deve passar pelo fluxo formal de Pull Request, suíte de testes (`make test`) e aprovação pelo merge gate / auditor humano.
