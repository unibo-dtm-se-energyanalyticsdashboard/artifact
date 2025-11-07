set -euo pipefail
: "${DB_HOST:?}"; : "${DB_PORT:?}"; : "${DB_USER:?}"; : "${DB_NAME:?}"
pg_dump --host="$DB_HOST" --port="$DB_PORT" --username="$DB_USER" \
  --data-only --no-owner --no-acl "$DB_NAME" > artifacts/data_dump.sql
