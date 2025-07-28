#!/bin/bash
set -e

echo "🔧 Installing AWS CLI..."
cd /tmp
curl -s "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip -q awscliv2.zip
sudo ./aws/install
echo "✅ AWS CLI installed: $(aws --version)"

echo "🐘 Installing PostgreSQL client..."
curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg
echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" | sudo tee /etc/apt/sources.list.d/pgdg.list
sudo apt update -y
sudo apt install -y postgresql-client-13 libpq-dev

echo "🌐 Getting external IP..."
export GITPOD_IP=$(curl -s ifconfig.me)
echo "GITPOD_IP=$GITPOD_IP"

echo "🔐 Updating RDS security group..."
if [ -f "$THEIA_WORKSPACE_ROOT/backend-flask/bin/rds-sg-rules-update" ]; then
  source "$THEIA_WORKSPACE_ROOT/backend-flask/bin/rds-sg-rules-update"
else
  echo "❌ rds-sg-rules-update script not found!"
fi

cd "$THEIA_WORKSPACE_ROOT"
