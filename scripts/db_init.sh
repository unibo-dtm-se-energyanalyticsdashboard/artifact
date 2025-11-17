#!/usr/bin/env bash
# --------------------------------------------------------------------------
# DATABASE INITIALIZATION SCRIPT (DDL Execution)
# This script executes the DDL (schema creation) using the psql client.
# It ensures the database structure is ready before data ingestion (Part 1).
# --------------------------------------------------------------------------

# Set script to "strict mode"
# -e: Exit immediately if any command fails.
# -u: Treat unset variables as an error.
# -o pipefail: Ensures that a pipeline command fails if any part of it fails.
set -euo pipefail

# Execute the psql command-line utility to run the schema file.
# The connection string is built dynamically using environment variables.
# It uses the ${VAR:-default} pattern to provide sensible defaults (e.g., localhost)
# if variables are not set in the environment (e.g., from a .env file).
psql "host=${PGHOST:-localhost} port=${PGPORT:-5432} user=${PGUSER:-postgres} dbname=${PGDATABASE:-energy_analytics} password=${PGPASSWORD:-Password123}" -f sql/01_schema.sql

# Print a success message to the console upon completion.
echo "DB initialized with your schema."