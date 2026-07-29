---
name: spec-kit
description: Guia completo, automação e comandos do GitHub Spec Kit e Spec-Driven Development (SDD) para especificação executável, desenvolvimento de software, gestão de extensões, integrações de agentes (Gemini, Claude, Codex, Copilot) e resolução de bugs.
---

# GitHub Spec Kit & Spec-Driven Development (SDD) Meta-Skill

Esta skill disponibiliza o fluxo de **Spec-Driven Development (SDD)** do GitHub Spec Kit para ser utilizado por qualquer agente em qualquer repositório.

---

## 📌 1. Inicialização do Projeto via CLI (`specify`)

Para bootstrap do Spec Kit em um projeto existente ou novo:

```bash
# Inicializar no diretório atual com integração Gemini CLI e scripts em Python:
specify init --here --integration gemini --script py

# Inicializar para Claude Code:
specify init --here --integration claude --script py

# Inicializar para Codex CLI (modo skills):
specify init --here --integration codex --integration-options="--skills"
```

---

## 🚀 2. Comandos e Fases do Ciclo SDD

Ao especificar e construir funcionalidades, execute os comandos do Spec Kit na seguinte sequência:

```text
/speckit.constitution ➔ /speckit.specify ➔ /speckit.clarify ➔ /speckit.plan ➔ /speckit.analyze ➔ /speckit.checklist ➔ /speckit.tasks ➔ /speckit.implement ➔ /speckit.converge
```

| Comando | Descrição & Propósito |
| :--- | :--- |
| **`/speckit.constitution`** | Define princípios arquiteturais, regras de segurança, qualidade e padrões de código (`.specify/constitution.md`). |
| **`/speckit.specify`** | Define requisitos funcionais, histórias de usuário e escopo sem assumir tecnologia (`.specify/spec.md`). |
| **`/speckit.clarify`** | Quiz interativo para identificar ambiguidades, lacunas e regras de negócio obscuras antes da arquitetura. |
| **`/speckit.plan`** | Elabora o plano técnico de implementação, stack tecnologica, estrutura de arquivos e modelos de dados (`.specify/plan.md`). |
| **`/speckit.analyze`** | Realiza análise cruzada de consistência entre a especificação, plano técnico e lista de tarefas. |
| **`/speckit.checklist`** | Gera critérios de aceite em linguagem clara ("testes para especificações") para validação manual ou automatizada. |
| **`/speckit.tasks`** | Decompõe o plano em tarefas acionáveis e ordenadas por dependência (`.specify/tasks.md`). |
| **`/speckit.taskstoissues`**| Converte as tarefas geradas em Issues no GitHub ou Gitea para acompanhamento de backlog. |
| **`/speckit.implement`** | Executa sequencialmente as tarefas construindo o código e testes do projeto. |
| **`/speckit.converge`** | Compara o código gerado contra os requisitos originais e cria tarefas remanescentes se necessário. |

---

## 🏗️ 3. Padrões Avançados (Monorepos, Specs Complexas e Bugfix)

### 🏬 Projetos Complexos & Monorepos ("Spec of Specs")
* Em projetos grandes ou monorepos, mantenha a especificação principal na raiz (`.specify/spec.md`) e crie sub-especificações por módulo em `.specify/modules/<modulo>/spec.md`.

### 🐛 Fluxo de Bugfix Agêntico (Agentic Bugfix Workflow)
Para corrigir bugs usando SDD:
1. Execute `/speckit.specify` descrevendo o comportamento esperado vs comportamento atual do bug.
2. Execute `/speckit.plan` isolando a causa raiz e os testes de regressão necessários.
3. Execute `/speckit.tasks` e `/speckit.implement` para corrigir e validar a suíte de testes.

---

## 🔧 4. Gerenciamento de Extensões e Presets

```bash
# Buscar extensões no catálogo:
specify extension search

# Instalar uma extensão aprovada:
specify extension add <nome-extensao>

# Listar extensões instaladas:
specify extension list

# Verificar atualização da CLI:
specify self check && specify self upgrade
```
