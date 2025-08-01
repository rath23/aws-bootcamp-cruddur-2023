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
# PostgreSQL Client Installation
####################################
echo "=== Installing PostgreSQL client ==="
# Add PostgreSQL signing key and repo
curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo gpg --dearmor -o /usr/share/keyrings/postgresql-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/postgresql-keyring.gpg] http://apt.postgresql.org/pub/repos/apt \
  $(lsb_release -cs)-pgdg main" | sudo tee /etc/apt/sources.list.d/postgresql.list
sudo apt-get update
sudo apt-get install -y postgresql-client-13 libpq-dev

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
# Install docker CLI package; if already present this is a no-op
sudo apt-get install -y docker.io

# Ensure 'docker compose' is available (v2). If not, attempt to enable plugin.
if ! docker compose version >/dev/null 2>&1; then
  echo "docker compose not found; attempting to install Compose v2 plugin"
  DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
  mkdir -p "$DOCKER_CONFIG/cli-plugins"
  COMPOSE_VERSION="v2.22.0"  # adjust if you want a newer pinned version
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
