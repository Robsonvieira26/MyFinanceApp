#!/usr/bin/env bash
set -euo pipefail

# scripts/backup.sh — dump do Postgres em backups/ com rotação.
# Uso: ./scripts/backup.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

BACKUP_DIR="$ROOT_DIR/backups"
RETENTION=${BACKUP_RETENTION:-14}

if [ ! -f .env ]; then
  echo "ERRO: .env não encontrado em $ROOT_DIR" >&2
  exit 1
fi

set -a
# shellcheck disable=SC1091
source .env
set +a

: "${POSTGRES_USER:?POSTGRES_USER não definido em .env}"
: "${POSTGRES_DB:?POSTGRES_DB não definido em .env}"

mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +"%Y-%m-%d_%H%M%S")
OUTFILE="$BACKUP_DIR/finance_${TIMESTAMP}.sql.gz"

echo "▸ Gerando backup: $OUTFILE"
docker compose exec -T db pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists \
  | gzip > "$OUTFILE"

SIZE=$(du -h "$OUTFILE" | cut -f1)
echo "✓ Backup concluído: $OUTFILE ($SIZE)"

COUNT=$(ls -1 "$BACKUP_DIR"/finance_*.sql.gz 2>/dev/null | wc -l)
if [ "$COUNT" -gt "$RETENTION" ]; then
  TO_REMOVE=$((COUNT - RETENTION))
  echo "▸ Rotação: removendo $TO_REMOVE backup(s) antigo(s) (retenção=$RETENTION)"
  # shellcheck disable=SC2012
  ls -1t "$BACKUP_DIR"/finance_*.sql.gz | tail -n "$TO_REMOVE" | xargs -r rm -v
fi

echo "▸ Backups atuais:"
ls -lh "$BACKUP_DIR"/finance_*.sql.gz 2>/dev/null || true
