#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CURRENT_USER="$(id -un)"
SERVICE_NAME="notes-app"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

echo "Creating systemd service..."
echo "  User:              $CURRENT_USER"
echo "  Working directory: $SCRIPT_DIR"

sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Notes App
After=network.target

[Service]
User=$CURRENT_USER
WorkingDirectory=$SCRIPT_DIR
ExecStart=python3 $SCRIPT_DIR/main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

echo "Service file written to $SERVICE_FILE"

echo "Reloading systemd..."
sudo systemctl daemon-reload

echo "Enabling $SERVICE_NAME service..."
sudo systemctl enable "$SERVICE_NAME"

echo "Starting $SERVICE_NAME service..."
sudo systemctl start "$SERVICE_NAME"

echo ""
sudo systemctl status "$SERVICE_NAME"

echo ""
echo "Done. '$SERVICE_NAME' is running and will start automatically on boot."
