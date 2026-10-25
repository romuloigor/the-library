set dotenv-load := true

# List available commands
default:
    @just --list

# Install the library (first-time setup)
install:
    claude --dangerously-skip-permissions --model opus "/library install"

# Add a new skill, agent, or prompt to the catalog
add prompt:
    claude --dangerously-skip-permissions --model opus "/library add {{prompt}}"

# Pull a skill from the catalog (install or refresh)
use name:
    claude --dangerously-skip-permissions --model opus "/library use {{name}}"

# Push local changes back to the source
push name:
    claude --dangerously-skip-permissions --model opus "/library push {{name}}"

# Remove a locally installed skill
remove name:
    claude --dangerously-skip-permissions --model opus "/library remove {{name}}"

# Sync all installed items (re-pull from source)
sync:
    claude --dangerously-skip-permissions --model opus "/library sync"

# List all entries in the catalog with install status
list:
    claude --dangerously-skip-permissions --model opus "/library list"

# Search the catalog by keyword
search keyword:
    claude --dangerously-skip-permissions --model opus "/library search {{keyword}}"

# Instala o git hook de sync do ai-memory no repositório da Wiki (Air ou Mini)
install-wiki-hook wiki_path="/Users/romuloigor/Local/usit-developer-guide.wiki":
    @mkdir -p "{{wiki_path}}/.git/hooks"
    @cp hooks/wiki-post-commit-aimemory-sync.sh "{{wiki_path}}/.git/hooks/post-commit"
    @chmod +x "{{wiki_path}}/.git/hooks/post-commit"
    @echo "✅ Hook post-commit de sincronização com ai-memory instalado em {{wiki_path}}/.git/hooks/post-commit"

# Lista hooks gerenciados pelo the-library
hooks:
    @echo "📦 Hooks no catálogo the-library:"
    @ls -l hooks/

