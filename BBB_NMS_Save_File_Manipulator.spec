# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['BBB_NMS_Save_File_Manipulator.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\MBIN_PROJECTS\\Working_Projects\\BBB-NMS-SFM-Project\\help', 'help')],
    hiddenimports=['imports'],
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
    name='BBB_NMS_Save_File_Manipulator',
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
)