# Set script to "strict mode"
# -e: Exit immediately if any command fails.
# -u: Treat unset variables as an error.
# -o pipefail: Ensures that a pipeline command fails if any part of it fails.
set -euo pipefail

# Check for mandatory environment variables.
# If any are unset (e.g., DB_HOST), the script will exit with an error.
: "${DB_HOST:?}"; : "${DB_PORT:?}"; : "${DB_USER:?}"; : "${DB_NAME:?}"

# Execute the pg_dump command to create a data-only backup.
pg_dump --host="$DB_HOST" --port="$DB_PORT" --username="$DB_USER" \
  --data-only \
  --no-owner \
  --no-acl \
  "$DB_NAME" > artifacts/data_dump.sql

# --data-only: Dumps only the data, not the schema (DDL).
# --no-owner / --no-acl: Improves compatibility for restoring the dump.
# > artifacts/data_dump.sql: Redirects the SQL output to the deliverables folder.