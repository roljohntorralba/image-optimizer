# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

block_cipher = None

# Get the path to the script
script_path = Path('image_optimizer.py')

a = Analysis(
    [str(script_path)],
    pathex=[],
    binaries=[],
    datas=[
        ('README.md', '.'),
        ('LICENSE', '.'),
    ],
    hiddenimports=[
        'PIL._tkinter_finder',
        'pillow_avif',
    ],
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
    [],
    exclude_binaries=True,
    name='Rols Image Optimizer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Rols Image Optimizer',
)

# Create macOS app bundle
app = BUNDLE(
    coll,
    name='Rols Image Optimizer.app',
    icon=None,
    bundle_identifier='com.roljohntorralba.image-optimizer',
    version='1.2.1',
    info_plist={
        'CFBundleName': 'Rols Image Optimizer',
        'CFBundleDisplayName': 'Rol\'s Image Optimizer',
        'CFBundleIdentifier': 'com.roljohntorralba.image-optimizer',
        'CFBundleVersion': '1.2.1',
        'CFBundleShortVersionString': '1.2.1',
        'NSHighResolutionCapable': True,
        'LSApplicationCategoryType': 'public.app-category.photography',
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'Image Files',
                'CFBundleTypeRole': 'Editor',
                'LSHandlerRank': 'Alternate',
                'LSItemContentTypes': [
                    'public.image',
                    'public.jpeg',
                    'public.png',
                    'com.compuserve.gif',
                    'public.tiff',
                    'com.microsoft.bmp',
                ]
            }
        ],
    },
)
