#!/usr/bin/env bash
set -euo pipefail

# scripts/update.sh — atualiza a aplicação.
# Faz: backup → git pull → rebuild → up -d → alembic upgrade head

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

echo "═════════════════════════════════════════"
echo " MyFinanceApp · update $(date +'%Y-%m-%d %H:%M:%S')"
echo "═════════════════════════════════════════"
echo ""

if ! docker compose ps --quiet db | grep -q .; then
  echo "AVISO: container db não está rodando — pulando backup."
  SKIP_BACKUP=1
else
  SKIP_BACKUP=0
fi

if [ "$SKIP_BACKUP" -eq 0 ]; then
  echo "▸ [1/5] Backup automático pré-update"
  "$SCRIPT_DIR/backup.sh"
  echo ""
fi

echo "▸ [2/5] git pull origin main"
git fetch origin
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)
if [ "$LOCAL" = "$REMOTE" ]; then
  echo "  (já atualizado)"
else
  git pull --ff-only origin main
fi
echo ""

echo "▸ [3/5] docker compose build"
docker compose build
echo ""

echo "▸ [4/5] docker compose up -d"
docker compose up -d
echo ""

echo "▸ aguardando Postgres ficar pronto..."
for _ in $(seq 1 30); do
  if docker compose exec -T db pg_isready -U "${POSTGRES_USER:-finance}" -d "${POSTGRES_DB:-finance}" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

echo "▸ [5/5] alembic upgrade head"
docker compose exec -T web alembic upgrade head
echo ""

echo "═════════════════════════════════════════"
echo "✓ Update concluído"
echo "═════════════════════════════════════════"
docker compose ps
