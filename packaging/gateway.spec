import os
import sys

from PyInstaller.utils.hooks import collect_submodules, copy_metadata

block_cipher = None

root = os.path.abspath(os.path.join(SPECPATH, ".."))
gateway_entry = os.path.join(root, "kordevance", "gateway_runner.py")
cli_entry = os.path.join(root, "kordevance", "cli", "main.py")
icon_map = {
    "win32": os.path.join(SPECPATH, "windows", "icon.ico"),
    "darwin": os.path.join(SPECPATH, "macos", "icon.icns"),
}
icon = icon_map.get(sys.platform)
icon = icon if icon and os.path.exists(icon) else None

hiddenimports = (
    collect_submodules("keyring.backends")
    + collect_submodules("pydantic_ai")
    + [
        "uvicorn.lifespan.on",
        "uvicorn.lifespan.off",
        "uvicorn.protocols.http.h11_impl",
        "uvicorn.protocols.websockets.wsproto_impl",
        "uvicorn.loops.auto",
        "aiosqlite",
        "greenlet",
    ]
)

datas = (
    copy_metadata("genai_prices")
    + copy_metadata("pydantic-ai")
    + copy_metadata("pydantic-ai-slim")
    + copy_metadata("kordevance")
)

# --- kordevance-gateway (background service) ---

gateway_analysis = Analysis(
    [gateway_entry],
    pathex=[root],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    cipher=block_cipher,
)

gateway_pyz = PYZ(gateway_analysis.pure, cipher=block_cipher)

gateway_exe = EXE(
    gateway_pyz,
    gateway_analysis.scripts,
    [],
    exclude_binaries=True,
    name="kordevance-gateway",
    console=True,
    icon=icon,
)

# --- kordi (CLI) ---

cli_analysis = Analysis(
    [cli_entry],
    pathex=[root],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    cipher=block_cipher,
)

cli_pyz = PYZ(cli_analysis.pure, cipher=block_cipher)

cli_exe = EXE(
    cli_pyz,
    cli_analysis.scripts,
    [],
    exclude_binaries=True,
    name="kordi",
    console=True,
    icon=icon,
)

# Both executables ship side by side in one COLLECT so they share the
# (large) pydantic-ai/uvicorn dependency tree instead of duplicating it.
coll = COLLECT(
    gateway_exe,
    gateway_analysis.binaries,
    gateway_analysis.datas,
    cli_exe,
    cli_analysis.binaries,
    cli_analysis.datas,
    name="kordevance",
)
