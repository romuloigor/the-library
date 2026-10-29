---
name: elephant-goldfish-model
description: Metodologia e workflows do Google Elephant-Goldfish Model (EGM) para Spec-Driven Development, separando sessões com memória ampla (Elephant) de revisões adversariais sem contexto (Goldfish).
---

# Elephant-Goldfish Model (EGM) Skill

Esta habilidade implementa os fluxos de trabalho e padrões conceituais do **Google Elephant-Goldfish Model** (`google/elephant-goldfish-model`) adaptados para a Squad Antigravity e para o repositório `the-library`.

## 🐘 1. O Conceito Fundamental
O EGM resolve o problema de poluição de contexto e viés de confirmação no desenvolvimento assistido por IA ao desacoplar duas personas com níveis opostos de retenção de memória:

- **The Elephant (Memória Longa / Visão Sistêmica):** Retém o contexto global do repositório, diretrizes de governança, restrições arquiteturais e histórico de sessões. Responsável pelo brainstorm e pela redação de especificações rigorosas. **O Elefante nunca escreve código diretamente.**
- **The Goldfish (Zero-Context / Stateless Swarm):** Subagentes efêmeros iniciados sem memória da sessão de brainstorming. Avaliam exclusivamente o documento de especificação gerado e os artefatos reais do repositório para apontar falhas, ambiguidades, riscos de segurança e premissas não declaradas.

---

## 🛠️ 2. Workflows e Ações Disponíveis

### Ação 1: `/egm-brainstorm` (Elephant)
- **Objetivo:** Explorar o escopo do problema, restrições operacionais e levantar hipóteses antes de qualquer implementação.
- **Entradas:** Descrição do problema ou ID da Issue.
- **Saída:** Documento preliminar de conceito com requisitos, trade-offs e limites de atuação.

### Ação 2: `/egm-spec-draft` (Elephant)
- **Objetivo:** Converter o conceito em especificação formal (`docs/designs/*.md` ou `.specify/spec.md`).
- **Diretriz:** Seções modulares cobrindo Arquitetura, Contratos de API/Interface, Critérios de Aceite e Gestão de Riscos (OWASP/Segurança).

### Ação 3: `/egm-goldfish-review` (Goldfish Swarm)
- **Objetivo:** Disparar um subagente independente com prompt limpo para revisar a especificação.
- **Lentes de Análise:**
  1. *Compreensibilidade:* O texto é autoexplicativo sem conhecimento prévio da conversa?
  2. *Casos Extremos & Falhas:* Falhas de rede, limites de taxa, concorrência e idempotência.
  3. *Segurança & Zero-Mock:* Conformidade estrita com Zero-Mock e OWASP Top 10.
  4. *Viabilidade de Implementação:* O escopo é realista para a sprint/issue atual?

### Ação 4: `/egm-drift-check` (Auditoria Pós-Build)
- **Objetivo:** Comparar os arquivos modificados/adicionados no Git em relação à especificação aprovada.
- **Saída:** Relatório indicando divergências não autorizadas (Scope Creep) ou requisitos não atendidos.

---

## 📋 3. Matriz de Integração com Squad USIT Support

| Papel EGM | Ator no Squad | Canal / Ferramenta |
| :--- | :--- | :--- |
| **Elephant (Design)** | Antigravity Linux / Antigravity Mini | `ai-memory`, Wiki SSoT, `.specify/` |
| **Builder (Implementação)** | Antigravity Mini (Compute Node M4) | Código-fonte, testes unitários (`make test`) |
| **Goldfish (Reviewer / QA)** | Antigravity Air (QA / Cyber) | CodeMender, auditoria independente de Aceite |
| **Drift Checker** | Antigravity Air | Validação de Critérios de Aceite pré-fechamento |
