#!/usr/bin/env python3
import sys
import os
import argparse
import subprocess
import shutil

def run_cmd(cmd_list, cwd=None, check=False):
    print(f"🚀 Execution: {' '.join(cmd_list)}")
    try:
        res = subprocess.run(cmd_list, cwd=cwd, capture_output=True, text=True)
        if res.returncode != 0 and check:
            print(f"⚠️ Erro ao executar {cmd_list[0]}: {res.stderr.strip()}")
            sys.exit(1)
        return res.returncode == 0, res.stdout.strip(), res.stderr.strip()
    except Exception as e:
        if check:
            print(f"❌ Falha crítica: {e}")
            sys.exit(1)
        return False, "", str(e)

def clean_param(val):
    if not val:
        return val
    if "=" in str(val):
        key, _, rest = str(val).partition("=")
        if key.lstrip("-") in ("org", "name", "description", "path", "private"):
            return rest.strip('"\'')
    return str(val).strip('"\'')

def main():
    parser = argparse.ArgumentParser(description="Bootstrapper de Novo Projeto SaaS no Gitea")
    parser.add_argument("--org", default="britsuporte", help="Organização no Gitea (padrão: britsuporte)")
    parser.add_argument("--name", required=True, help="Nome do repositório/SaaS")
    parser.add_argument("--description", default="", help="Descrição do projeto SaaS")
    parser.add_argument("--path", default="", help="Caminho local para clone (padrão: ~/Local/<name>)")
    args = parser.parse_args()

    org = clean_param(args.org) or "britsuporte"
    name = clean_param(args.name)
    raw_path = clean_param(args.path)
    desc = clean_param(args.description) or f"Projeto SaaS {name}"
    target_path = os.path.expanduser(raw_path) if raw_path else os.path.expanduser(f"~/Local/{name}")

    print("=" * 70)
    print(f"🚀 INICIALIZANDO NOVO PROJETO SAAS: {org}/{name}")
    print(f"📂 Diretório Local: {target_path}")
    print("=" * 70)

    # 1. Criar repositório no Gitea
    guide_dir = "/Users/romuloigor/Local/usit-developer-guide"
    helper_script = os.path.join(guide_dir, "scripts", "gitea_helper.py")
    
    print("\n1️⃣  Criando repositório no Gitea (Privado: true)...")
    run_cmd(["python3", helper_script, "create-repo", "--org", org, "--name", name, "--description", desc, "--private", "true"], check=False)

    # 2. Preparar pasta local e clone/init git
    print("\n2️⃣  Configurando diretório local...")
    os.makedirs(target_path, exist_ok=True)

    clone_url = f"http://mini:3000/{org}/{name}.git"
    if not os.path.exists(os.path.join(target_path, ".git")):
        print(f"Clonando {clone_url}...")
        ok, out, err = run_cmd(["git", "clone", clone_url, "."], cwd=target_path)
        if not ok:
            print("Inicializando repositório git localmente...")
            run_cmd(["git", "init"], cwd=target_path)
            run_cmd(["git", "remote", "add", "origin", clone_url], cwd=target_path)

    # 3. Inicializar Spec Kit (specify init)
    print("\n3️⃣  Inicializando o Spec Kit (specify init)...")
    specify_bin = shutil.which("specify") or os.path.expanduser("~/.local/bin/specify")
    if os.path.exists(specify_bin) or shutil.which("specify"):
        run_cmd(["specify", "init", "--here", "--integration", "gemini", "--script", "py", "--force"], cwd=target_path)
    else:
        print("⚠️ CLI specify não encontrada. Execute 'specify init' manualmente após a instalação.")

    # 4. Copiar AGENTS.md e .agents/
    print("\n4️⃣  Provisionando AGENTS.md e diretrizes da Squad...")
    src_agents_md = os.path.join(guide_dir, "AGENTS.md")
    dst_agents_md = os.path.join(target_path, "AGENTS.md")
    if os.path.exists(src_agents_md):
        shutil.copy2(src_agents_md, dst_agents_md)

    src_agents_dir = os.path.join(guide_dir, ".agents")
    dst_agents_dir = os.path.join(target_path, ".agents")
    if os.path.exists(src_agents_dir):
        if os.path.exists(dst_agents_dir):
            shutil.rmtree(dst_agents_dir)
        shutil.copytree(src_agents_dir, dst_agents_dir)

    src_gemini_dir = os.path.join(guide_dir, ".gemini")
    dst_gemini_dir = os.path.join(target_path, ".gemini")
    if os.path.exists(src_gemini_dir):
        if not os.path.exists(dst_gemini_dir):
            shutil.copytree(src_gemini_dir, dst_gemini_dir)
        else:
            src_cmd = os.path.join(src_gemini_dir, "commands")
            dst_cmd = os.path.join(dst_gemini_dir, "commands")
            if os.path.exists(src_cmd):
                os.makedirs(dst_cmd, exist_ok=True)
                for f in os.listdir(src_cmd):
                    shutil.copy2(os.path.join(src_cmd, f), os.path.join(dst_cmd, f))

    # 5. Provisionar justfile e submódulos just/
    print("\n5️⃣  Provisionando justfile e módulos just...")
    src_just_dir = os.path.join(guide_dir, "just")
    dst_just_dir = os.path.join(target_path, "just")
    if os.path.exists(src_just_dir):
        if os.path.exists(dst_just_dir):
            shutil.rmtree(dst_just_dir)
        shutil.copytree(src_just_dir, dst_just_dir)

    justfile_content = f"""set dotenv-load := true

# Importação dos Módulos Oficiais da Squad Antigravity
mod gitea 'just/gitea.just'
mod cmux 'just/cmux.just'
mod gemini 'just/gemini.just'
mod tailscale 'just/tailscale.just'

# Listar todos os comandos disponíveis
default:
    @just --list

# Executar suíte de testes do projeto
test:
    @echo "🧪 Executando suíte de testes..."

# Iniciar agente mestre para este projeto SaaS
mestre:
    python3 /Users/romuloigor/Local/usit-developer-guide/scripts/mestre_launcher.py --org {org} --repo {name}
"""
    with open(os.path.join(target_path, "justfile"), "w") as f:
        f.write(justfile_content)

    # 6. Criar Workspace no cmux (se disponível)
    print("\n6️⃣  Configurando Workspace no cmux...")
    if shutil.which("cmux"):
        run_cmd(["cmux", "workspace", "create", "--name", f"{org}/{name}", "--cwd", target_path])

    # 7. Commit inicial e Push para o Gitea
    print("\n7️⃣  Realizando commit inicial e push para o Gitea...")
    run_cmd(["git", "add", "-A"], cwd=target_path)
    run_cmd(["git", "commit", "-m", "feat: initialize SaaS project with Spec Kit, AGENTS.md, justfile and cmux rules"], cwd=target_path)
    run_cmd(["git", "branch", "-M", "main"], cwd=target_path)
    run_cmd(["git", "push", "-u", "origin", "main"], cwd=target_path)

    print("\n" + "=" * 70)
    print(f"✅ PROJETO SAAS '{org}/{name}' INICIALIZADO COM SUCESSO!")
    print(f"🔗 Repositório Gitea: {clone_url}")
    print(f"📂 Diretório Local: {target_path}")
    print(f"📖 Wiki SSoT: http://mini:3000/usitsupport/usit-developer-guide/wiki/DEVELOPER_GUIDE")
    print("=" * 70)

if __name__ == "__main__":
    main()
