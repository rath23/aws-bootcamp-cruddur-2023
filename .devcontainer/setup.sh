#!/bin/bash
set -euo pipefail

echo "=== Installing prerequisite packages ==="
sudo apt-get update
sudo apt-get install -y ca-certificates gnupg lsb-release unzip curl software-properties-common

####################################
# AWS CLI Installation
####################################
echo "=== Installing AWS CLI ==="
cd /tmp
curl -sL "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip -q awscliv2.zip
sudo ./aws/install --update
rm -rf awscliv2.zip aws
echo "AWS CLI version:"
aws --version

####################################
# PostgreSQL Client Installation with HTTPS and fallback
####################################
echo "=== Installing PostgreSQL client ==="
CODENAME=$(lsb_release -cs)
PG_REPO_LINE="deb [signed-by=/usr/share/keyrings/postgresql-keyring.gpg] https://apt.postgresql.org/pub/repos/apt ${CODENAME}-pgdg main"

# Add signing key
curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo gpg --dearmor -o /usr/share/keyrings/postgresql-keyring.gpg

# Try adding the external PGDG repo and updating
echo "$PG_REPO_LINE" | sudo tee /etc/apt/sources.list.d/postgresql.list
set +e
sudo apt-get update
UPDATE_EXIT=$?
set -e

if [ $UPDATE_EXIT -ne 0 ]; then
  echo "WARNING: External PostgreSQL APT repo failed to update (maybe unavailable for ${CODENAME}-pgdg). Falling back to the distro packaged client."
  sudo rm -f /etc/apt/sources.list.d/postgresql.list
  sudo apt-get update
  sudo apt-get install -y postgresql-client libpq-dev
else
  sudo apt-get install -y postgresql-client-13 libpq-dev
fi

# sanity check
if ! command -v psql >/dev/null; then
  echo "ERROR: psql not found after installation" >&2
  exit 1
fi
echo "psql version: $(psql --version)"

####################################
# Docker CLI (for using docker / docker compose)
####################################
echo "=== Installing Docker CLI (will use host daemon if socket is mounted) ==="
sudo apt-get install -y docker.io

if ! docker compose version >/dev/null 2>&1; then
  echo "docker compose not found; attempting to install Compose v2 plugin"
  DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
  mkdir -p "$DOCKER_CONFIG/cli-plugins"
  COMPOSE_VERSION="v2.22.0"
  curl -SL "https://github.com/docker/compose/releases/download/$COMPOSE_VERSION/docker-compose-linux-x86_64" -o /tmp/docker-compose
  chmod +x /tmp/docker-compose
  mv /tmp/docker-compose "$DOCKER_CONFIG/cli-plugins/docker-compose"
fi

echo "Docker version:"
docker version || true
echo "Docker Compose version:"
docker compose version || echo "docker compose still unavailable"

####################################
# Update RDS Security Group Rules (if applicable)
####################################
if [ -n "${CODESPACE_VSCODE_FOLDER-}" ] && [ -f "$CODESPACE_VSCODE_FOLDER/backend-flask/bin/rds-sg-rules-update" ]; then
    echo "=== Updating RDS security group rules ==="
    export GITPOD_IP=$(curl -s ifconfig.me)
    # shellcheck source=/dev/null
    source "$CODESPACE_VSCODE_FOLDER/backend-flask/bin/rds-sg-rules-update"
fi

echo "=== Environment setup complete! ==="


# import { checkAuth } from '../lib/CheckAuth';
