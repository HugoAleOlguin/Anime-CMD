# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = [
    'src',
    'src.core',
    'src.core.config',
    'src.core.models',
    'src.core.db',
    'src.core.player',
    'src.providers',
    'src.providers.base',
    'src.providers.animeonline',
    'src.providers.tioanime',
    'src.providers.monoschinos',
    'src.providers.jkanime',
    'src.providers.secret',
    'src.providers.registry',
    'src.extractors',
    'src.extractors.base',
    'src.extractors.streamtape',
    'src.extractors.streamwish',
    'src.extractors.mp4upload',
    'src.extractors.yourupload',
    'src.extractors.voex',
    'src.extractors.mediafire',
    'src.extractors.registry',
    'src.ui',
    'src.ui.theme',
    'src.ui.fzf',
    'src.ui.printer',
    'bs4',
    'curl_cffi',
]

# Recolectar datos y binarios de curl_cffi para evitar errores de certificados o librerías dinámicas
try:
    cffi_datas, cffi_binaries, cffi_hidden = collect_all('curl_cffi')
    datas += cffi_datas
    binaries += cffi_binaries
    hiddenimports += cffi_hidden
except Exception:
    pass

try:
    bs4_datas, bs4_binaries, bs4_hidden = collect_all('bs4')
    datas += bs4_datas
    binaries += bs4_binaries
    hiddenimports += bs4_hidden
except Exception:
    pass

block_cipher = None

a = Analysis(
    ['../src/main.py'],
    pathex=['..'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='anime',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None
)
