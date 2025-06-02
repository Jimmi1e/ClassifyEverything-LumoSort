# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('models/ViT-B-32.pt', 'models'),
        ('clip_vocab/bpe_simple_vocab_16e6.txt.gz', 'clip_vocab'),
        ('clip/bpe_simple_vocab_16e6.txt.gz', 'clip'),
        ('icon/logo.png', 'icon')
    ],
    hiddenimports=['clip.simple_tokenizer'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='LumoSort',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon\\logo.ico'],
)