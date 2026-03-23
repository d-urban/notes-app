#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
CURRENT_USER="$(id -un)"
PYTHON_BIN="$(which python3)"
SERVICE_NAME="notes-app"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
WSL_CONF="/etc/wsl.conf"

check_wsl_conf() {
    # Extract the content of the [boot] section (between [boot] and next section or EOF)
    boot_block=$(awk '/^\[boot\]/{found=1; next} found && /^\[/{exit} found{print}' "$WSL_CONF" 2>/dev/null)
    boot_exists=$(grep -c '^\[boot\]' "$WSL_CONF" 2>/dev/null || true)

    if [ "$boot_exists" -gt 0 ]; then
        # [boot] section exists — inspect it
        if echo "$boot_block" | grep -q '^systemd=true'; then
            # Case 1: [boot] exists and systemd=true is correctly set under it
            echo "[wsl.conf] systemd is already enabled under [boot]. OK."
        elif echo "$boot_block" | grep -q '^systemd='; then
            # Case 3b: systemd= exists under [boot] but is not =true
            echo ""
            echo "ERROR: /etc/wsl.conf has a [boot] section with a 'systemd=' entry"
            echo "       but it is not set to 'true'. Please update it manually:"
            echo ""
            echo "  [boot]"
            echo "  systemd=true"
            echo ""
            exit 1
        else
            # Case 3a: [boot] exists but no systemd= key at all — safe to add it
            echo "[wsl.conf] [boot] section found but 'systemd=true' is missing. Adding it..."
            sudo awk '/^\[boot\]/{print; print "systemd=true"; next} {print}' "$WSL_CONF" | sudo tee "$WSL_CONF.tmp" > /dev/null
            sudo mv "$WSL_CONF.tmp" "$WSL_CONF"
            echo "[wsl.conf] 'systemd=true' added under [boot]."
            echo ""
            echo "NOTE: You must restart WSL for systemd to take effect before the"
            echo "      service will auto-start on boot. Run in PowerShell/CMD: wsl --shutdown"
        fi
    else
        # Case 2: no [boot] section — append it
        echo "[wsl.conf] No [boot] section found. Appending [boot] and systemd=true..."
        printf '\n[boot]\nsystemd=true\n' | sudo tee -a "$WSL_CONF" > /dev/null
        echo "[wsl.conf] Done."
        echo ""
        echo "NOTE: You must restart WSL for systemd to take effect before the"
        echo "      service will auto-start on boot. Run in PowerShell/CMD: wsl --shutdown"
    fi
}

check_wsl_conf

echo ""
echo "Creating systemd service..."
echo "  User:              $CURRENT_USER"
echo "  Working directory: $ROOT_DIR"

sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Notes App
After=network.target

[Service]
User=$CURRENT_USER
WorkingDirectory=$ROOT_DIR
ExecStart=$PYTHON_BIN $ROOT_DIR/main.py
Restart=on-failure
KillMode=mixed
TimeoutStopSec=10

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
