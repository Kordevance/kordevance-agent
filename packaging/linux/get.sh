#!/bin/sh

set -eu

REPO="Kordevance/kordevance-agent"
API_URL="https://api.github.com/repos/${REPO}/releases/latest"
WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

case "$(uname -s)" in
    Linux) ;;
    *)
        echo "This installer is for Linux only. See https://kordevance.com/download for other platforms." >&2
        exit 1
        ;;
esac

case "$(uname -m)" in
    x86_64|amd64) ARCH="x86_64" ;;
    aarch64|arm64) ARCH="arm64" ;;
    *)
        echo "Unsupported architecture: $(uname -m)" >&2
        exit 1
        ;;
esac

ASSET_NAME="kordevance-linux-${ARCH}.tar.gz"

echo "Fetching latest release metadata..."
DOWNLOAD_URL="$(
    curl -fsSL "$API_URL" \
        | grep "\"browser_download_url\":.*${ASSET_NAME}\"" \
        | head -n1 \
        | sed -E 's/.*"([^"]+)".*/\1/'
)"

if [ -z "$DOWNLOAD_URL" ]; then
    echo "Could not find a release asset named ${ASSET_NAME}." >&2
    exit 1
fi

echo "Downloading ${ASSET_NAME}..."
curl -fsSL "$DOWNLOAD_URL" -o "$WORK_DIR/kordevance.tar.gz"

echo "Extracting..."
tar -xzf "$WORK_DIR/kordevance.tar.gz" -C "$WORK_DIR"

echo "Installing (you may be prompted for your password)..."
sudo sh "$WORK_DIR/kordevance/install.sh"
