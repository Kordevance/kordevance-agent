#!/bin/sh

#   sudo /Applications/Kordevance/uninstall.sh
set -eu

if [ "$(id -u)" -ne 0 ]; then
    echo "uninstall.sh must be run as root (try: sudo $0)" >&2
    exit 1
fi

INSTALL_DIR="/Applications/Kordevance"
BIN_DIR="/usr/local/bin"
REAL_USER="${SUDO_USER:-$(stat -f%Su /dev/console)}"
REAL_HOME="$(eval echo "~$REAL_USER")"
PLIST_DEST="$REAL_HOME/Library/LaunchAgents/com.kordevance.gateway.plist"
DATA_DIR="$REAL_HOME/.kordevance"

if [ -f "$PLIST_DEST" ]; then
    echo "Stopping kordevance-gateway..."
    sudo -u "$REAL_USER" launchctl unload "$PLIST_DEST" 2>/dev/null || true
    rm -f "$PLIST_DEST"
fi

if [ -x "$INSTALL_DIR/kordi" ] && [ -d "$DATA_DIR" ]; then
    sudo -u "$REAL_USER" "$INSTALL_DIR/kordi" purge-keyring --yes 2>/dev/null || true
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
