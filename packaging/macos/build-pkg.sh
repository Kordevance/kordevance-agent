#!/bin/sh

set -eu

ARCH="${ARCH:?ARCH must be set (arm64 or x86_64)}"
VERSION="${VERSION:?VERSION must be set}"
MACOS_APP_SIGN_IDENTITY="${MACOS_APP_SIGN_IDENTITY:?MACOS_APP_SIGN_IDENTITY must be set}"
MACOS_INSTALLER_CERT_P12_BASE64="${MACOS_INSTALLER_CERT_P12_BASE64:?MACOS_INSTALLER_CERT_P12_BASE64 must be set}"
MACOS_INSTALLER_CERT_PASSWORD="${MACOS_INSTALLER_CERT_PASSWORD:?MACOS_INSTALLER_CERT_PASSWORD must be set}"
NOTARY_API_KEY_BASE64="${NOTARY_API_KEY_BASE64:?NOTARY_API_KEY_BASE64 must be set}"
NOTARY_KEY_ID="${NOTARY_KEY_ID:?NOTARY_KEY_ID must be set}"
NOTARY_ISSUER_ID="${NOTARY_ISSUER_ID:?NOTARY_ISSUER_ID must be set}"
KEYCHAIN="${KEYCHAIN:?KEYCHAIN must be set}"

SPECPATH_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
ROOT_DIR="$(CDPATH= cd -- "$SPECPATH_DIR/.." && pwd)"
DIST_DIR="$ROOT_DIR/dist/kordevance"
STAGE_DIR="$ROOT_DIR/dist/pkg-root/Applications/Kordevance"
SCRIPTS_DIR="$ROOT_DIR/dist/pkg-scripts"
OUT_PKG="$ROOT_DIR/dist/Kordevance-${ARCH}.pkg"

rm -rf "$ROOT_DIR/dist/pkg-root" "$SCRIPTS_DIR"
mkdir -p "$STAGE_DIR" "$SCRIPTS_DIR"

cp -R "$DIST_DIR"/. "$STAGE_DIR"/
cp "$SPECPATH_DIR/macos/com.kordevance.gateway.plist" "$STAGE_DIR/"
cp "$SPECPATH_DIR/macos/uninstall.sh" "$STAGE_DIR/"
chmod +x "$STAGE_DIR/uninstall.sh" "$STAGE_DIR/kordevance-gateway" "$STAGE_DIR/kordi"
cp "$SPECPATH_DIR/macos/install.sh" "$SCRIPTS_DIR/postinstall"
chmod +x "$SCRIPTS_DIR/postinstall"

echo "Code-signing bundled binaries..."

find "$STAGE_DIR" -type f -print0 | while IFS= read -r -d '' f; do
    case "$(file -b "$f")" in
        Mach-O*)
            codesign --force --options runtime --timestamp \
                --sign "$MACOS_APP_SIGN_IDENTITY" \
                --keychain "$KEYCHAIN" \
                "$f"
            ;;
    esac
done

echo "Code-signing entry binaries with entitlements..."
codesign --force --options runtime --timestamp \
    --entitlements "$SPECPATH_DIR/macos/entitlements.plist" \
    --sign "$MACOS_APP_SIGN_IDENTITY" \
    --keychain "$KEYCHAIN" \
    "$STAGE_DIR/kordevance-gateway" "$STAGE_DIR/kordi"

echo "Building component package (unsigned, we sign it with rcodesign next)..."
pkgbuild \
    --root "$ROOT_DIR/dist/pkg-root" \
    --scripts "$SCRIPTS_DIR" \
    --identifier com.kordevance.gateway \
    --version "$VERSION" \
    --install-location / \
    "$OUT_PKG"

echo "Signing pkg with rcodesign..."
WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT

echo "$MACOS_INSTALLER_CERT_P12_BASE64" | base64 --decode > "$WORKDIR/installer_cert.p12"
rcodesign sign \
    --p12-file "$WORKDIR/installer_cert.p12" \
    --p12-password "$MACOS_INSTALLER_CERT_PASSWORD" \
    "$OUT_PKG"
rm "$WORKDIR/installer_cert.p12"

echo "Notarizing and stapling..."
echo "$NOTARY_API_KEY_BASE64" | base64 --decode > "$WORKDIR/notary_key.p8"
rcodesign encode-app-store-connect-api-key \
    -o "$WORKDIR/notary_key.json" \
    "$NOTARY_ISSUER_ID" "$NOTARY_KEY_ID" "$WORKDIR/notary_key.p8"
rm "$WORKDIR/notary_key.p8"

rcodesign notary-submit \
    --api-key-file "$WORKDIR/notary_key.json" \
    --staple \
    "$OUT_PKG"
rm "$WORKDIR/notary_key.json"

echo "Built $OUT_PKG"
