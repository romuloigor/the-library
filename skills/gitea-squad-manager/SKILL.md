---
name: gitea-squad-manager
description: Gerenciamento da Squad Antigravity no Gitea (issues, notificações, comentários, repositórios, wiki) e bootstrapping automatizado de projetos SaaS via just new-saas.
---

# Gitea Squad Manager & Bootstrapper SaaS

Skill para interação com a instância local do Gitea (`http://mini:3000` / `http://localhost:3000`), criação de repositórios para organizações (`britsuporte`, `usitsupport`) e bootstrapping automatizado de novos projetos SaaS.

---

## 📌 Principais Capacidades

1. **Criação de Repositórios & SaaS**: Criar novos repositórios em organizações e inicializar a esteira completa (Spec Kit + cmux + AGENTS.md + justfile).
2. **Notificações ('Gitea News')**: Consultar notificações não lidas.
3. **Gestão de Issues (Definition of Done)**: Listar, criar, comentar e fechar Issues com suporte ao protocolo Anti-Loop.
4. **Wiki Central (SSoT)**: Listar e consultar páginas da Wiki de Arquitetura.
5. **Agente Mestre**: Disparar o Agente Mestre em um workspace dedicado do `cmux`.

---

## 🛠️ Comandos & Atalhos via Terminal (`just` / Python)

| Ação | Comando `just` | Comando Python direto |
| :--- | :--- | :--- |
| **Novo Projeto SaaS** | `just new-saas org="britsuporte" name="meu-saas"` | `python3 scripts/new_saas_bootstrapper.py --org britsuporte --name meu-saas` |
| **Criar Repositório** | `just gitea create-repo org="britsuporte" name="meu-repo"` | `python3 scripts/gitea_helper.py create-repo --org britsuporte --name meu-repo` |
| **Notificações** | `just gitea news` | `python3 scripts/gitea_helper.py news` |
| **Listar Issues** | `just gitea issues state=open` | `python3 scripts/gitea_helper.py issues --repo usitsupport/usit-developer-guide` |
| **Criar Issue** | `just gitea create-issue title="..." body="..."` | `python3 scripts/gitea_helper.py create-issue --title "..." --body "..."` |
| **Fechar Issue** | `just gitea close-issue issue_id=X` | `python3 scripts/gitea_helper.py close-issue --issue X` |
| **Iniciar Mestre** | `just mestre org=usitsupport repo=usit-developer-guide` | `python3 scripts/mestre_launcher.py --org usitsupport --repo usit-developer-guide` |

---

## 🔑 Autenticação & Configuração

* O helper busca automaticamente o token em `~/.gitea_mini_token` (no Mac Mini) ou `~/.gitea_air_token` ou pela variável de ambiente `GITEA_TOKEN`.
* A URL padrão do Gitea é `http://mini:3000` (ou customizada via variável `GITEA_URL`).
