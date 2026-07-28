---
name: gitea-squad-manager
description: Gerenciamento da Squad Antigravity no Gitea (issues, notificações, comentários, wiki central) e acionamento do Agente Mestre via cmux.
---

# Gitea Squad Manager & Agente Mestre

Skill para interação com a instância local do Gitea (`http://mini:3000` / `http://localhost:3000`) e controle da Squad de Agentes da organização `usitsupport`.

---

## 📌 Principais Capacidades

1. **Notificações ('Gitea News')**: Consultar notificações não lidas.
2. **Gestão de Issues (Definition of Done)**: Listar, criar, comentar e fechar Issues com suporte ao protocolo Anti-Loop.
3. **Wiki Central (SSoT)**: Listar e consultar páginas da Wiki de Arquitetura.
4. **Agente Mestre**: Disparar o Agente Mestre em um workspace dedicado do `cmux`.

---

## 🛠️ Comandos & Atalhos via Terminal (`just` / Python)

| Ação | Comando Python direto |
| :--- | :--- |
| **Notificações** | `python3 scripts/gitea_helper.py news` |
| **Listar Issues** | `python3 scripts/gitea_helper.py issues --repo usitsupport/usit-developer-guide` |
| **Ler Comentários** | `python3 scripts/gitea_helper.py comments --issue X` |
| **Criar Issue** | `python3 scripts/gitea_helper.py create-issue --title "..." --body "..." --assignee "antigravity-bot-mini"` |
| **Comentar em Issue** | `python3 scripts/gitea_helper.py comment-issue --issue X --body "..."` |
| **Fechar Issue** | `python3 scripts/gitea_helper.py close-issue --issue X` |
| **Listar Wiki** | `python3 scripts/gitea_helper.py wiki` |
| **Iniciar Mestre** | `python3 scripts/mestre_launcher.py --org usitsupport --repo usit-developer-guide` |

---

## 🔑 Autenticação & Configuração

* O helper busca automaticamente o token em `~/.gitea_mini_token` (no Mac Mini) ou `~/.gitea_air_token` ou pela variável de ambiente `GITEA_TOKEN`.
* A URL padrão do Gitea é `http://mini:3000` (ou customizada via variável `GITEA_URL`).
