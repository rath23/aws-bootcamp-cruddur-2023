#!/bin/bash
set -e

echo "🔧 AWS CLI version:"
aws --version

# ⛅ Set public IP and run your script
export GITPOD_IP=$(curl -s ifconfig.me)
echo "🌐 GITPOD_IP: $GITPOD_IP"

# 👇 Make sure the script exists before sourcing
if [[ -f "$CODESPACE_VSCODE_FOLDER/backend-flask/bin/rds-sg-rules-update" ]]; then
  echo "🔐 Running RDS security group update script..."
  source "$CODESPACE_VSCODE_FOLDER/backend-flask/bin/rds-sg-rules-update"
else
  echo "⚠️ rds-sg-rules-update not found, skipping."
fi
