#!/usr/bin/env bash
set -euo pipefail
psql "host=${PGHOST:-localhost} port=${PGPORT:-5432} user=${PGUSER:-postgres} dbname=${PGDATABASE:-energy_analytics} password=${PGPASSWORD:-Password123}" -f sql/01_schema.sql
echo "DB initialized with your schema."
