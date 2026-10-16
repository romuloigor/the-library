---
name: ai-mem-wiki
description: "Consulta semântica e recuperação FTS5 de diretivas, padrões arquiteturais e guias na Fonte Única da Verdade (SSoT) do squad via ai-memory. Use `ai-mem-wiki \"<assunto>\"` para consultar a Wiki central (`usit-wiki`) ou `ai-mem --project <nome> \"<assunto>\"` para escopos específicos."
metadata:
  preferred-model: "Gemini 3.8 Flash"
  preferred-model-id: "gemini-3.8-flash"
  profile-alias: "/ai-mem-wiki"
---

# 🧠 Skill: ai-mem-wiki (Pesquisa SSoT na Wiki Central via ai-memory)

Esta skill define as instruções operacionais para que agentes autônomos e desenvolvedores realizem **Lazy Retrieval** de diretivas, decisões arquiteturais (Martin Fowler, OWASP, SRE), infraestrutura (Tailscale, Caddy, Mac Mini) e governança armazenadas na Wiki Central da Squad Antigravity (`usit-wiki`).

---

## 🎯 1. Quando Ativar esta Skill

Ative esta skill sempre que:
1. Precisar consultar regras, padrões ou guias da Squad (ex: portas, IPs do Tailscale, diretivas de commit, protocolo Anti-Loop, padrão Gemini 3.8 Flash).
2. O usuário solicitar: `pesquise na wiki`, `consulte a SSoT`, `ai-mem-wiki "<assunto>"` ou `ai-mem "<assunto>"`.
3. Antes de iniciar refatorações estruturais ou propor decisões arquiteturais, para conferir se já existe um padrão ou ADR estabelecido na Wiki.

---

## 💻 2. Modos de Uso

### A. Via Terminal CLI (`ai-mem-wiki` / `ai-mem`)

O utilitário está linkado no PATH global (`~/.local/bin/`):

```bash
# 1. Pesquisa direta na Wiki Central (SSoT da Squad)
ai-mem-wiki "anti-loop cmux"
ai-mem-wiki "fowler arquitetura"
ai-mem-wiki "100.86.22.127"

# 2. Usando o atalho ai-mem (consulta a Wiki por padrão)
ai-mem "padrao gemini flash"

# 3. Pesquisar em outro projeto ou repositório específico
ai-mem --project local-ai-memory "setup inicial"
ai-mem --project terraform-gcp-infra "wif provider"

# 4. Formato JSON (para pipelines ou parsing estruturado)
ai-mem-wiki --json "gitea webhooks"
```

### B. Via Ferramentas MCP (`memory_query`)

Quando operando dentro do Antigravity, Claude Code ou Codex com MCP ativo:
- Chame a ferramenta `memory_query`:
  ```json
  {
    "query": "termo de busca aqui",
    "scopes": [{"workspace": "default", "project": "usit-wiki"}]
  }
  ```

---

## 📐 3. Boas Práticas de Lazy Retrieval

1. **Evite Carregar Arquivos Inteiros sem Necessidade:**
   - Faça uma busca preliminar com `ai-mem-wiki "<termo>"`.
   - Se os snippets retornados já responderem à dúvida, use a informação diretamente sem ler dezenas de kilobytes de arquivo.
2. **Prioridade da SSoT:**
   - As regras da Wiki indexadas no projeto `usit-wiki` têm precedência sobre palpites ou suposições de treino do modelo.
3. **Sincronização:**
   - Se novos guias forem adicionados à Wiki no Git, execute `just sync-wiki-memory` para re-indexar os novos arquivos atômica e instantaneamente.

---

## 🛠️ 4. Scripts e Binários

- **Helper Executável:** `/Users/romuloigor/Local/the-library/skills/ai-mem-wiki/scripts/ai-mem-wiki`
- **Symlinks Globais:** `~/.local/bin/ai-mem-wiki` e `~/.local/bin/ai-mem`
- **Script de Sincronização:** `/Users/romuloigor/Local/local-ai-memory/scripts/sync_wiki_to_aimemory.py`
