# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files

# Collect all required PyQt5 data files
pyqt5_datas = collect_data_files('PyQt5')

a = Analysis(
    ['BBB_NMS_Save_File_Manipulator.py'],
    pathex=['C:\\MBIN_PROJECTS\\Working_Projects\\BBB-NMS-SFM-Project'],
    binaries=[],
    datas=[
    ('help', 'help'),
    ('images', 'images'),
    ('app_preferences.ini', '.'),
    ('reference_explorer.json', '.'),
    ('reference_fighter.json', '.'),
    ('reference_hauler.json', '.'),
    ('reference_living.json', '.'),
    ('reference_royal.json', '.'),
    ('reference_sentinel.json', '.'),
    ('reference_shuttle.json', '.'),
    ('reference_solar.json', '.'),
    ] + pyqt5_datas,
    hiddenimports=['imports'],  # Ensure 'imports' is a valid module
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

#coll = COLLECT(
#    exe,
#    a.binaries,
#    a.datas,
#    strip=False,
#    upx=True,
#    upx_exclude=[],
#    name='BBB_NMS_Save_File_Manipulator',
#)