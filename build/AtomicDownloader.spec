# -*- mode: python ; coding: utf-8 -*-
"""
Atomic Downloader - PyInstaller Build Spec
Creates a professional single-file Windows EXE.
"""
import os, sys

block_cipher = None
APP_DIR = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    [os.path.join(APP_DIR, '..', 'launcher.py')],
    pathex=[os.path.join(APP_DIR, '..')],
    binaries=[],
    datas=[
        # Templates
        (os.path.join(APP_DIR, '..', 'templates'), 'templates'),
        # Static files (CSS, JS, images, locales)
        (os.path.join(APP_DIR, '..', 'static'), 'static'),
        # Python modules
        (os.path.join(APP_DIR, '..', 'app.py'), '.'),
        (os.path.join(APP_DIR, '..', 'downloader_logic.py'), '.'),
        (os.path.join(APP_DIR, '..', 'cookie_manager.py'), '.'),
        (os.path.join(APP_DIR, '..', 'localization.py'), '.'),
        (os.path.join(APP_DIR, '..', 'utils.py'), '.'),
        (os.path.join(APP_DIR, '..', 'main.py'), '.'),
        (os.path.join(APP_DIR, '..', 'run.py'), '.'),
    ],
    hiddenimports=[
        'flask',
        'flask.json',
        'jinja2',
        'markupsafe',
        'webview',
        'webview.platforms.winforms',
        'webview.platforms.edgechromium',
        'clr_loader',
        'pythonnet',
        'yt_dlp',
        'requests',
        'packaging',
        'packaging.version',
        'selenium',
        'webdriver_manager',
        'tkinter',
        'tkinter.ttk',
        'tkinter.font',
        'ctypes',
        'ctypes.windll',
        'engineio.async_drivers.threading',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'numpy', 'scipy', 'pandas',
        'PIL', 'cv2', 'torch', 'tensorflow',
        'notebook', 'IPython', 'jupyter',
    ],
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
    name='AtomicDownloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,              # No console window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(APP_DIR, '..', 'static', 'images', 'logo.ico'),
    version=os.path.join(APP_DIR, 'version_info.txt'),
)
