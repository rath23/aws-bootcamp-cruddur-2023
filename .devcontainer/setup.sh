#!/bin/bash

# AWS CLI Installation
echo "Installing AWS CLI..."
cd /tmp
curl -sL "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip -q awscliv2.zip
sudo ./aws/install --update
rm -rf awscliv2.zip aws
aws --version

# PostgreSQL Client Installation
echo "Installing PostgreSQL client..."
curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo gpg --dearmor -o /usr/share/keyrings/postgresql-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/postgresql-keyring.gpg] http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" | sudo tee /etc/apt/sources.list.d/postgresql.list
sudo apt-get update
sudo apt-get install -y postgresql-client-13 libpq-dev

# Update RDS Security Group Rules
if [ -f "$CODESPACE_VSCODE_FOLDER/backend-flask/bin/rds-sg-rules-update" ]; then
    export GITPOD_IP=$(curl -s ifconfig.me)
    source "$CODESPACE_VSCODE_FOLDER/backend-flask/bin/rds-sg-rules-update"
fi

echo "Environment setup complete!"
