#!/usr/bin/env python3
import sys
import os
import argparse
import urllib.request
import json
import socket

GITEA_URL = "http://mini:3000"

def get_token():
    hostname = socket.gethostname().lower()
    if 'mini' in hostname:
        token_path = os.path.expanduser('~/.gitea_mini_token')
    else:
        token_path = os.path.expanduser('~/.gitea_air_token')
        
    if os.path.exists(token_path):
        return open(token_path).read().strip()
    return os.getenv('GITEA_TOKEN', '')

def request(path, method='GET', data=None):
    token = get_token()
    url = f"{GITEA_URL}/api/v1{path}"
    headers = {'Authorization': f'token {token}', 'Content-Type': 'application/json'}
    payload = json.dumps(data).encode('utf-8') if data else None
    
    req = urllib.request.Request(url, data=payload, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status == 204:
                return {}
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"⚠️ Erro na requisição [{method} {path}]: {e}")
        sys.exit(1)

def cmd_news(args):
    print("📰 === NOTIFICAÇÕES DO GITEA ('GITEA NEWS') ===")
    notifs = request('/notifications')
    if not notifs:
        print("✅ Nenhuma notificação pendente!")
        return
    for n in notifs:
        subj = n.get('subject', {})
        print(f" - [{subj.get('type')}] {subj.get('title')}")
        print(f"   URL: {n.get('repository', {}).get('html_url')}/issues/{subj.get('url', '').split('/')[-1]}\n")

def cmd_list_issues(args):
    repo = args.repo or "usitsupport/usit-developer-guide"
    print(f"📌 === ISSUES DO REPOSITÓRIO {repo} ===")
    issues = request(f'/repos/{repo}/issues?state={args.state}')
    if not issues:
        print("Nenhuma issue encontrada.")
        return
    for i in issues:
        assignee = (i.get('assignee') or {}).get('username', 'Ninguém')
        creator = (i.get('user') or {}).get('username', 'Desconhecido')
        print(f" #{i.get('number')} [{i.get('state', '').upper()}] {i.get('title')}")
        print(f"   Atribuído a: @{assignee} | Criador: @{creator}")
        print(f"   Link: {i.get('html_url')}\n")

def cmd_comments(args):
    repo = args.repo or "usitsupport/usit-developer-guide"
    print(f"💬 === COMENTÁRIOS DA ISSUE #{args.issue} ({repo}) ===")
    comments = request(f'/repos/{repo}/issues/{args.issue}/comments')
    if not comments:
        print("Nenhum comentário encontrado.")
        return
    for c in comments:
        user = c.get('user', {}).get('username')
        created = c.get('created_at')
        body = c.get('body')
        print(f"💬 Por @{user} em {created}:")
        print(f"{body}\n")
        print("-" * 50)

def cmd_create_issue(args):
    repo = args.repo or "usitsupport/usit-developer-guide"
    payload = {
        'title': args.title,
        'body': args.body,
        'assignees': [args.assignee] if args.assignee else []
    }
    res = request(f'/repos/{repo}/issues', method='POST', data=payload)
    print(f"✅ Issue #{res.get('number')} criada com sucesso!")
    print(f"🔗 Link: {res.get('html_url')}")

def cmd_comment_issue(args):
    repo = args.repo or "usitsupport/usit-developer-guide"
    payload = {'body': args.body}
    res = request(f'/repos/{repo}/issues/{args.issue}/comments', method='POST', data=payload)
    print(f"💬 Comentário adicionado na Issue #{args.issue} com sucesso!")

def cmd_close_issue(args):
    repo = args.repo or "usitsupport/usit-developer-guide"
    payload = {'state': 'closed'}
    res = request(f'/repos/{repo}/issues/{args.issue}', method='PATCH', data=payload)
    print(f"🔒 Issue #{args.issue} fechada com sucesso!")

def clean_param(val):
    if not val:
        return val
    if "=" in str(val):
        key, _, rest = str(val).partition("=")
        if key.lstrip("-") in ("org", "name", "description", "path", "private"):
            return rest.strip('"\'')
    return str(val).strip('"\'')

def cmd_create_repo(args):
    org = clean_param(args.org) or "britsuporte"
    name = clean_param(args.name)
    desc = clean_param(args.description) if args.description else f"Repositório {name}"
    payload = {
        'name': name,
        'description': desc,
        'private': str(args.private).lower() in ('true', '1', 'yes'),
        'auto_init': True,
        'default_branch': 'main'
    }
    print(f"🚀 Criando repositório '{org}/{name}' no Gitea ({GITEA_URL})...")
    res = request(f'/orgs/{org}/repos', method='POST', data=payload)
    print(f"✅ Repositório '{org}/{res.get('name', name)}' criado com sucesso!")
    print(f"🔗 Link: {res.get('html_url')}")
    print(f"📦 Clone URL: {res.get('clone_url')}")

def cmd_members(args):
    print("👥 === MEMBROS DA ORGANIZAÇÃO USITSUPPORT ===")
    members = request('/orgs/usitsupport/members')
    for m in members:
        print(f" - @{m.get('username')} ({m.get('full_name', 'Sem nome')})")

def cmd_wiki(args):
    repo = args.repo or "usitsupport/usit-developer-guide"
    if args.page:
        res = request(f'/repos/{repo}/wiki/page/{args.page}')
        import base64
        content = base64.b64decode(res.get('content_base64', '')).decode('utf-8')
        author = res.get('last_commit', {}).get('author', {}).get('name')
        print(f"📖 === PÁGINA DA WIKI: {res.get('title')} ({repo}) ===")
        print(f"Último commit por: {author}")
        print("-" * 50)
        print(content)
        return
    print(f"📚 === PÁGINAS DA WIKI DE {repo} ===")
    pages = request(f'/repos/{repo}/wiki/pages')
    for p in pages:
        print(f" - {p.get('title')} (Último commit por: {p.get('last_commit', {}).get('author', {}).get('name')})")

def ensure_webhook(repo_full_name, port=5001):
    owner, repo = repo_full_name.split('/', 1) if '/' in repo_full_name else ('usitsupport', repo_full_name)
    repo_name = repo
    webhook_url = f"http://100.86.22.127:{port}"
    
    events = [
        "issues",
        "issue_comment",
        "issue_assign",
        "pull_request",
        "pull_request_comment",
        "pull_request_review_request"
    ]

    try:
        hooks = request(f"/repos/{owner}/{repo}/hooks")
        existing_hook = None
        if isinstance(hooks, list):
            existing_hook = next((h for h in hooks if h.get('config', {}).get('url') == webhook_url or f":{port}" in h.get('config', {}).get('url', '')), None)

        payload = {
            "name": repo_name,
            "type": "gitea",
            "config": {
                "url": webhook_url,
                "content_type": "json"
            },
            "events": events,
            "active": True
        }

        if existing_hook:
            hook_id = existing_hook['id']
            request(f"/repos/{owner}/{repo}/hooks/{hook_id}", method="PATCH", data=payload)
            return True, webhook_url, f"Webhook '{repo_name}' (ID {hook_id}) atualizado com sucesso."
        else:
            new_hook = request(f"/repos/{owner}/{repo}/hooks", method="POST", data=payload)
            return True, webhook_url, f"Webhook '{repo_name}' criado com sucesso (ID {new_hook.get('id')})."
    except Exception as e:
        return False, webhook_url, str(e)

def get_issue_session_id_from_gitea(repo_full_name, issue_num, issue_obj=None):
    """
    Busca nas labels da Issue do Gitea se já existe uma label de sessão no formato 'session:<session_id>'.
    Retorna a string session_id ou None.
    """
    labels = []
    if issue_obj and 'labels' in issue_obj:
        labels = issue_obj.get('labels', [])
    else:
        try:
            res = request(f"/repos/{repo_full_name}/issues/{issue_num}")
            if res and isinstance(res, dict):
                labels = res.get('labels', [])
        except Exception:
            pass
            
    for lbl in labels:
        name = lbl.get('name', '')
        if name.startswith('session:'):
            return name.split('session:', 1)[1]
        elif name.startswith('session-id:'):
            return name.split('session-id:', 1)[1]
    return None

def ensure_issue_session_label(repo_full_name, issue_num, session_id):
    """
    Garante que a label 'session:<session_id>' esteja criada no repositório e atrelada à Issue no Gitea.
    """
    label_name = f"session:{session_id}"
    try:
        # 1. Verificar se a label já existe no repositório
        repo_labels = request(f"/repos/{repo_full_name}/labels")
        target_label = None
        if isinstance(repo_labels, list):
            target_label = next((l for l in repo_labels if l.get('name') == label_name), None)
        
        if not target_label:
            # Criar label no repositório
            target_label = request(f"/repos/{repo_full_name}/labels", method='POST', data={
                'name': label_name,
                'color': '0088cc',
                'description': f'ID de sessão do agente agy para a Issue #{issue_num}'
            })
            
        if target_label and target_label.get('id'):
            # 2. Atrelar a label na Issue
            request(f"/repos/{repo_full_name}/issues/{issue_num}/labels", method='POST', data={
                'labels': [target_label['id']]
            })
            return True, f"Label '{label_name}' atrelada à Issue #{issue_num}"
    except Exception as e:
        return False, f"Erro ao atrelar label na Issue #{issue_num}: {e}"
    return False, "Não foi possível atrelar a label."

def ensure_issue_cmux_label(repo_full_name, issue_num, cmux_workspace):
    """
    Garante que a label 'cmux:<cmux_workspace>' esteja criada no repositório e atrelada à Issue no Gitea.
    """
    label_name = f"cmux:{cmux_workspace}"
    try:
        repo_labels = request(f"/repos/{repo_full_name}/labels")
        target_label = None
        if isinstance(repo_labels, list):
            target_label = next((l for l in repo_labels if l.get('name') == label_name), None)
        
        if not target_label:
            target_label = request(f"/repos/{repo_full_name}/labels", method='POST', data={
                'name': label_name,
                'color': '006b6b',
                'description': f'Workspace cmux executando a Issue #{issue_num}'
            })
            
        if target_label and target_label.get('id'):
            request(f"/repos/{repo_full_name}/issues/{issue_num}/labels", method='POST', data={
                'labels': [target_label['id']]
            })
            return True, f"Label '{label_name}' atrelada à Issue #{issue_num}"
    except Exception as e:
        return False, f"Erro ao atrelar label cmux na Issue #{issue_num}: {e}"
    return False, "Não foi possível atrelar a label cmux."

def main():
    parser = argparse.ArgumentParser(description="CLI Helper para Gitea Squad Workflow")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("news", help="Ver notícias/notificações pendentes")
    
    p_list = subparsers.add_parser("issues", help="Listar issues")
    p_list.add_argument("--repo", default="usitsupport/usit-developer-guide")
    p_list.add_argument("--state", default="open")

    p_comm = subparsers.add_parser("comments", help="Ver comentários de uma issue")
    p_comm.add_argument("--issue", required=True)
    p_comm.add_argument("--repo", default="usitsupport/usit-developer-guide")

    p_create = subparsers.add_parser("create-issue", help="Criar nova issue")
    p_create.add_argument("--title", required=True)
    p_create.add_argument("--body", required=True)
    p_create.add_argument("--assignee", default="")
    p_create.add_argument("--repo", default="usitsupport/usit-developer-guide")

    p_comment = subparsers.add_parser("comment-issue", help="Comentar em issue")
    p_comment.add_argument("--issue", required=True)
    p_comment.add_argument("--body", required=True)
    p_comment.add_argument("--repo", default="usitsupport/usit-developer-guide")

    p_close = subparsers.add_parser("close-issue", help="Fechar issue")
    p_close.add_argument("--issue", required=True)
    p_close.add_argument("--repo", default="usitsupport/usit-developer-guide")

    p_create_repo = subparsers.add_parser("create-repo", help="Criar novo repositório na organização")
    p_create_repo.add_argument("--org", default="britsuporte", help="Organização no Gitea")
    p_create_repo.add_argument("--name", required=True, help="Nome do repositório")
    p_create_repo.add_argument("--description", default="", help="Descrição do repositório")
    p_create_repo.add_argument("--private", default="true", help="Repositório privado (true/false)")

    subparsers.add_parser("members", help="Listar membros da organização")

    p_wiki = subparsers.add_parser("wiki", help="Listar ou visualizar páginas da wiki")
    p_wiki.add_argument("--repo", default="usitsupport/usit-developer-guide")
    p_wiki.add_argument("--page", default=None, help="Nome da página da wiki para exibir o conteúdo")

    args = parser.parse_args()

    commands = {
        "news": cmd_news,
        "issues": cmd_list_issues,
        "comments": cmd_comments,
        "create-issue": cmd_create_issue,
        "comment-issue": cmd_comment_issue,
        "close-issue": cmd_close_issue,
        "create-repo": cmd_create_repo,
        "members": cmd_members,
        "wiki": cmd_wiki
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
