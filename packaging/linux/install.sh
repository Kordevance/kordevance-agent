#!/bin/sh

set -eu

if [ "$(id -u)" -ne 0 ]; then
    echo "install.sh must be run as root (try: sudo sh install.sh)" >&2
    exit 1
fi

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
INSTALL_DIR="/opt/kordevance"
BIN_DIR="/usr/local/bin"
SERVICE_USER="${SUDO_USER:-${USER:-root}}"
UNIT_SRC="$SCRIPT_DIR/kordevance-gateway.service"
UNIT_DEST="/etc/systemd/system/kordevance-gateway.service"

if [ ! -x "$SCRIPT_DIR/kordevance-gateway" ] || [ ! -x "$SCRIPT_DIR/kordi" ]; then
    echo "kordevance-gateway/kordi not found next to install.sh -- run install.sh from inside the extracted release directory." >&2
    exit 1
fi

echo "Installing to $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
cp -R "$SCRIPT_DIR"/. "$INSTALL_DIR"/
chmod +x "$INSTALL_DIR/kordevance-gateway" "$INSTALL_DIR/kordi" "$INSTALL_DIR/uninstall.sh"

echo "Linking kordi into $BIN_DIR..."
ln -sf "$INSTALL_DIR/kordi" "$BIN_DIR/kordi"

echo "Registering systemd service (user: $SERVICE_USER)..."
sed "s#__SERVICE_USER__#$SERVICE_USER#g; s#__INSTALL_DIR__#$INSTALL_DIR#g" "$UNIT_SRC" > "$UNIT_DEST"

systemctl daemon-reload
systemctl enable --now kordevance-gateway

echo
echo "Done. kordevance-gateway is running in the background and will start on boot."
echo "Run 'kordi --help' to get started."
echo "To uninstall later: sudo $INSTALL_DIR/uninstall.sh"
