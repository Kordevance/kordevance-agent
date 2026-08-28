#!/bin/sh

set -eu

INSTALL_DIR="/Applications/Kordevance"
BIN_DIR="/usr/local/bin"

REAL_USER="${SUDO_USER:-$(stat -f%Su /dev/console)}"
REAL_HOME="$(eval echo "~$REAL_USER")"
LOG_DIR="$REAL_HOME/Library/Logs/Kordevance"
PLIST_SRC="$INSTALL_DIR/com.kordevance.gateway.plist"
PLIST_DEST="$REAL_HOME/Library/LaunchAgents/com.kordevance.gateway.plist"

mkdir -p "$LOG_DIR"
mkdir -p "$REAL_HOME/Library/LaunchAgents"
chown "$REAL_USER" "$LOG_DIR"

sed -e "s#__INSTALL_DIR__#$INSTALL_DIR#g" -e "s#__LOG_DIR__#$LOG_DIR#g" "$PLIST_SRC" > "$PLIST_DEST"
chown "$REAL_USER" "$PLIST_DEST"

echo "Linking kordi into $BIN_DIR..."
mkdir -p "$BIN_DIR"
ln -sf "$INSTALL_DIR/kordi" "$BIN_DIR/kordi"

echo "Starting kordevance-gateway as $REAL_USER..."
sudo -u "$REAL_USER" launchctl unload "$PLIST_DEST" 2>/dev/null || true
sudo -u "$REAL_USER" launchctl load "$PLIST_DEST"

echo
echo "Done. kordevance-gateway is running in the background and will start at login."
echo "Run 'kordi --help' to get started."
echo "To uninstall later: sudo $INSTALL_DIR/uninstall.sh"
