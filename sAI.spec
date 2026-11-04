# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller specification file for sAI (Scalable AI Interface) v1.0.0
Builds a standalone, relocatable Windows 64-bit desktop application directory.
"""

from __future__ import annotations

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Base directory
SPEC_ROOT = Path('.').resolve()

# CustomTkinter font and theme assets
customtkinter_datas = collect_data_files('customtkinter')

# Core application resource files (read-only assets)
datas = customtkinter_datas + [
    (str(SPEC_ROOT / 'Logo.png'), '.'),
    (str(SPEC_ROOT / 'assets' / 'icon.ico'), 'assets'),
]

# Hidden imports for dynamic/runtime UI and backend modules
hiddenimports = [
    'customtkinter',
    'darkdetect',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'httpx',
    'httpcore',
    'dotenv',
    'rich',
    'rich.console',
    'rich.panel',
    'schedule',
    'backend.config',
    'backend.storage',
    'backend.settings',
    'backend.model_manager',
    'backend.assistant',
    'backend.memory',
    'backend.profile_memory',
    'backend.desktop',
    'backend.file_manager',
    'backend.providers',
    'backend.llm',
    'frontend.app',
    'frontend.sidebar',
    'frontend.chat',
    'frontend.settings',
    'frontend.about',
    'frontend.memory',
    'frontend.search',
    'frontend.vision',
    'frontend.voice',
    'frontend.setup_wizard',
]

# Exclude heavy machine learning libraries and developer tools not used by the core app
# Also exclude pythoncom/win32com which fail pywin32 hook resolution on Python 3.14
excludes = [
    'torch',
    'torchvision',
    'transformers',
    'huggingface_hub',
    'safetensors',
    'onnxruntime',
    'scipy',
    'sklearn',
    'scikit-learn',
    'numba',
    'llvmlite',
    'matplotlib',
    'cv2',
    'opencv-python',
    'IPython',
    'jupyter_client',
    'jupyter_core',
    'tornado',
    'zmq',
    'pyzmq',
    'pandas',
    'openpyxl',
    'tensorboard',
    'notebook',
    'fastapi',
    'uvicorn',
    'starlette',
    'sounddevice',
    'soundfile',
    'pythoncom',
    'pywintypes',
    'win32com',
    'pyttsx3',
    'speech_recognition',
    'pyaudio',
]

a = Analysis(
    ['run.py'],
    pathex=[str(SPEC_ROOT), str(SPEC_ROOT / 'backend'), str(SPEC_ROOT / 'frontend')],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='sAI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(SPEC_ROOT / 'assets' / 'icon.ico'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='sAI',
)
