#!/usr/bin/env bash
# package_for_vps.sh
# Create a zip archive of the project prepared for deployment to VPS.
# Usage: ./scripts/package_for_vps.sh /path/to/output/sayt-deploy.zip
# Example: ./scripts/package_for_vps.sh ../sayt-deploy.zip

set -euo pipefail
OUT=${1:-../sayt-deploy.zip}
ROOT_DIR=$(dirname "$0")/.. 
cd "$ROOT_DIR"

# Files/dirs to exclude
EXCLUDES=(
  "--exclude=.venv/*"
  "--exclude=.git/*"
  "--exclude=*.pyc"
  "--exclude=__pycache__/*"
  "--exclude=*.sqlite3"
  "--exclude=media/*"
  "--exclude=deploy/*.key"
  "--exclude=*.log"
)

# Ensure .env.example is included but not .env
if [ -f .env ]; then
  echo "Warning: .env exists in repo root and will NOT be included in the zip. Ensure you copy .env.example and set values on VPS."
fi

echo "Creating zip: $OUT"
# Build exclude args
EX_ARG=()
for e in "${EXCLUDES[@]}"; do
  EX_ARG+=("$e")
done

# Use zip -r to create archive
zip -r "$OUT" . ${EX_ARG[@]}

echo "Created $OUT"

echo "Notes:"
echo " - The .env file is not included. Copy deploy/.env.example on VPS and configure DJANGO_SECRET_KEY, DJANGO_ALLOWED_HOSTS, etc."
echo " - After extracting on VPS, create a virtualenv, install requirements, run migrate and collectstatic, then configure systemd/nginx as described in deploy/README.md"
