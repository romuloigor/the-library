---
name: user-profile-and-preferences
description: Perfil profissional de Rômulo Igor, diretrizes operacionais, preferências de trabalho e contextos de projetos (Applied AI Engineer, OEC, SRE/DevOps, GCP, Tag Affinity).
---

# Perfil Profissional & Preferências de Trabalho do Usuário (Rômulo Igor)

Este skill consolida o perfil profissional, diretrizes operacionais e memórias de contexto para agentes de IA atuando com Rômulo Igor.

---

## 👤 Perfil & Posicionamento

* **Usuário:** Rômulo Igor
* **Experiência:** +20 anos em Engenharia de Software, Arquitetura Cloud (GCP/AWS), Segurança, SRE e DevOps.
* **Posicionamento Profissional (OEC):** **Applied AI Engineer** / **Forward Deployed AI Engineer**, mantendo DevOps/SRE como diferencial de entrega e execução.
* **Idioma Padrão:** Português do Brasil (PT-BR) para diálogos, explicações, documentações locais e postagens/copy.

---

## 🎯 Diretrizes Operacionais & Estilo de Entrega

1. **Evidência Empírica & Verificação em Código Real:**
   - Validar fontes reais no repositório (código, configs, logs) antes de fazer suposições.
   - Diagnosticar falhas a partir dos logs de erro reais e completos.

2. **Autonomia & Continuidade:**
   - Para erros diretos de compilação, pipeline ou script, avançar com correções end-to-end sem solicitar aprovações intermediárias redundantes.
   - Manter documentação do repositório (`README.md`, `docs/`) sempre sincronizada com o progresso das entregas.

3. **Segurança Mandatória:**
   - **Zero Vazamento de Credenciais:** Nunca exibir senhas, tokens ou chaves privadas em telas ou logs.
   - Manter isolamento de execução para scripts externos e respeitar políticas de segurança (`AI_JAIL`).

---

## 🛠️ Guia de Projetos & Ambientes Específicos

* **`usit-ge-observability`**:
  - Consultas BigQuery centradas na tabela `agentspace_native_usage_logs.userQuery`.
  - Validação de grafos em `INFORMATION_SCHEMA.PROPERTY_GRAPHS`.
  - Chave primária de identidade: `email_key`.

* **`usit-tagaffinity`**:
  - Contrato de API oficial em `libs/contracts/openapi.yaml`.
  - Checklist e fluxo de release iOS em `docs/IOS_APPSTORE_READINESS.md`.
  - Gates de validação local: `make ios-release-sim` e `make test-ios`.

* **`terraform-gcp-infra`**:
  - Inspeção de falhas via logs de apply no Azure DevOps.
  - Auditoria de custos e FinOps agrupados por `Project name`.

* **Mac Mini & Infraestrutura Local**:
  - Acesso remoto de tela via Tailscale (`100.86.22.127` / `romuloigors-mini`) e VNC.
  - Uso mandatório de `cmux` para execuções interativas em terminal/bash para transparência e acompanhamento em tempo real.
