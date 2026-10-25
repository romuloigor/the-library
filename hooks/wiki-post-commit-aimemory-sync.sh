#!/usr/bin/env bash
# ==============================================================================
# Git Hook: post-commit (Distribuído via the-library)
# Repositório Alvo: usit-developer-guide.wiki (Mac Air & Mac Mini)
# Dispara a sincronização automática da Wiki para o daemon local do ai-memory
# ==============================================================================

SCRIPT_SYNC="/Users/romuloigor/Local/local-ai-memory/scripts/sync_wiki_to_aimemory.py"

if [ -f "$SCRIPT_SYNC" ]; then
  echo "🧠 [ai-memory] Commit detectado na Wiki. Sincronizando memória semântica..."
  # Gera timestamp com milissegundos via python3 (compatível com macOS BSD date)
  TS=$(python3 -c 'from datetime import datetime; print(datetime.now().strftime("%Y%m%d-%H%M%S-%f")[:-3])')
  LOG="/tmp/aimemory_wiki_sync-${TS}.log"
  # -u: output sem buffer; nohup: processo resiliente ao encerramento do shell pai
  nohup python3 -u "$SCRIPT_SYNC" > "$LOG" 2>&1 &
  echo "✅ [ai-memory] Sincronização disparada em background (log: $LOG)."
fi
