#!/bin/sh

#   sudo /opt/kordevance/uninstall.sh
set -eu

if [ "$(id -u)" -ne 0 ]; then
    echo "uninstall.sh must be run as root (try: sudo $0)" >&2
    exit 1
fi

INSTALL_DIR="/opt/kordevance"
BIN_DIR="/usr/local/bin"
UNIT_DEST="/etc/systemd/system/kordevance-gateway.service"
SERVICE_USER="${SUDO_USER:-${USER:-root}}"
SERVICE_HOME="$(eval echo "~$SERVICE_USER")"
DATA_DIR="$SERVICE_HOME/.kordevance"

if systemctl list-unit-files kordevance-gateway.service >/dev/null 2>&1; then
    echo "Stopping kordevance-gateway..."
    systemctl disable --now kordevance-gateway 2>/dev/null || true
fi

if [ -f "$UNIT_DEST" ]; then
    rm -f "$UNIT_DEST"
    systemctl daemon-reload
fi

if [ -x "$INSTALL_DIR/kordi" ] && [ -d "$DATA_DIR" ]; then
    sudo -u "$SERVICE_USER" "$INSTALL_DIR/kordi" purge-keyring --yes 2>/dev/null || true
fi

if [ -L "$BIN_DIR/kordi" ]; then
    rm -f "$BIN_DIR/kordi"
fi

if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
fi

if [ -d "$DATA_DIR" ]; then
    echo "Removing local data at $DATA_DIR..."
    rm -rf "$DATA_DIR"
fi

echo "Kordevance has been removed."
