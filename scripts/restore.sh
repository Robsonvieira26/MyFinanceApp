#!/usr/bin/env bash
set -euo pipefail

# scripts/restore.sh — restaura dump do Postgres.
# Uso: ./scripts/restore.sh backups/finance_YYYY-MM-DD_HHMMSS.sql.gz

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

if [ $# -ne 1 ]; then
  echo "Uso: $0 <arquivo.sql.gz>" >&2
  exit 1
fi

DUMP_FILE="$1"
if [ ! -f "$DUMP_FILE" ]; then
  echo "ERRO: arquivo não encontrado: $DUMP_FILE" >&2
  exit 1
fi

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

echo "╔══════════════════════════════════════════════════════════╗"
echo "║                       ATENÇÃO                            ║"
echo "║                                                          ║"
echo "║  Esta operação vai APAGAR todos os dados atuais do       ║"
echo "║  banco '$POSTGRES_DB' e substituí-los pelo conteúdo de:  "
echo "║  $DUMP_FILE"
echo "║                                                          ║"
echo "║  Esta ação NÃO PODE ser desfeita sem outro backup.       ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
read -r -p "Digite 'yes' (minúsculas) para confirmar: " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
  echo "Cancelado."
  exit 0
fi

echo "▸ Parando container web..."
docker compose stop web

echo "▸ Restaurando dump..."
gunzip -c "$DUMP_FILE" \
  | docker compose exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1

echo "▸ Subindo web novamente..."
docker compose up -d web

echo "✓ Restauração concluída."
