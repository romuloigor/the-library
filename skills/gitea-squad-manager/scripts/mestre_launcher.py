#!/usr/bin/env python3
import sys
import argparse
import subprocess
import os
import json
import time

def run_cmd(cmd_list, check=False):
    try:
        res = subprocess.run(cmd_list, capture_output=True, text=True)
        return res.returncode == 0, res.stdout, res.stderr
    except Exception as e:
        return False, "", str(e)

def is_cmux_available():
    try:
        res = subprocess.run(["cmux", "list-workspaces", "--json"], capture_output=True, text=True, timeout=3)
        return res.returncode == 0
    except Exception:
        return False

def find_org_workspace(org_name):
    ok, out, _ = run_cmd(["cmux", "workspace", "list", "--json"])
    if ok and out:
        try:
            data = json.loads(out)
            for ws in data.get("workspaces", []):
                title = ws.get("title") or ws.get("custom_title") or ""
                if title == org_name:
                    return ws.get("ref")
        except Exception:
            pass
    return None

def ensure_org_workspace(org_name, cwd):
    ws_ref = find_org_workspace(org_name)
    if ws_ref:
        print(f"📁 Reutilizando Workspace cmux da Org '{org_name}' ({ws_ref})...")
        run_cmd(["cmux", "select-workspace", "--workspace", ws_ref])
        return ws_ref
    
    print(f"📁 Criando Workspace cmux da Org '{org_name}'...")
    ok, out, _ = run_cmd(["cmux", "workspace", "create", "--name", org_name, "--cwd", cwd, "--json"])
    if ok and out:
        try:
            ws_ref = json.loads(out).get("workspace_ref", org_name)
            return ws_ref
        except Exception:
            pass
    return org_name

def main():
    parser = argparse.ArgumentParser(description="Launcher do Agente Mestre no cmux / Terminal")
    parser.add_argument("--org", default="usitsupport", help="Organização no Gitea")
    parser.add_argument("--repo", default="usit-developer-guide", help="Repositório no Gitea")
    args, unknown = parser.parse_known_args()

    org = args.org
    repo = args.repo
    cwd = os.getcwd()

    print(f"🤖 === INICIANDO AGENTE MESTRE PARA {org}/{repo} ===")

    # 1. Hierarquia cmux: Workspace (--org usitsupport), Pane (--repo usit-developer-guide)
    ws_ref = None
    if is_cmux_available():
        ws_ref = ensure_org_workspace(org, cwd)
        run_cmd(["cmux", "set-status", "mestre", f"Mestre: {org}/{repo}", "--workspace", ws_ref, "--color", "#0088CC"])
        run_cmd(["cmux", "set-progress", "1.0", "--label", f"Monitorando {org}/{repo}", "--workspace", ws_ref])
        run_cmd(["cmux", "log", "--workspace", ws_ref, "--level", "info", f"Agente Mestre inicializado para {org}/{repo}"])
        run_cmd(["cmux", "notify", "--title", "Agente Mestre Ativo", "--subtitle", f"Org: {org} | Repo: {repo}", "--body", "Monitorando Webhooks do Gitea"])

    # 2. Cadastrar / Verificar Webhook no Gitea automaticamente
    print(f"🔗 Verificando Webhook no Gitea para {org}/{repo}...")
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        import gitea_helper as gh
        ok, hk_url, msg = gh.ensure_webhook(f"{org}/{repo}")
        if ok:
            print(f"✅ Webhook Gitea verificado/cadastrado com sucesso: {hk_url} ({msg})")
        else:
            print(f"⚠️ Erro ao verificar Webhook no Gitea: {msg}")
    except Exception as e:
        print(f"⚠️ Aviso ao verificar Webhook no Gitea: {e}")

    # 3. Encerrar qualquer instância anterior na porta 5001
    subprocess.run(["pkill", "-f", "gitea_webhook_receiver.py"], capture_output=True)
    time.sleep(0.5)

    # 4. Iniciar Webhook Receiver em FOREGROUND escutando na porta 5001 com logs ao vivo
    print(f"\n📡 [AGENTE MESTRE] Escutando eventos do Gitea na porta 5001 (Foreground Mode)")
    print(f"📌 Pressione Ctrl+C para encerrar o Agente Mestre.\n")
    print("-" * 70)

    receiver_script = os.path.join(cwd, "scripts", "gitea_webhook_receiver.py")
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    try:
        proc = subprocess.Popen([sys.executable, receiver_script], env=env)
        proc.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 [AGENTE MESTRE] Encerrado pelo usuário (Ctrl+C).")
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except Exception:
            proc.kill()
        print("✅ Servidor do Agente Mestre finalizado.")

if __name__ == "__main__":
    main()
