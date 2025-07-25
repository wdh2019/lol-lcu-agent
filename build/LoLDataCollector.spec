# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec文件，用于定制构建过程
"""

import sys
import os
from PyInstaller.building.api import PYZ, EXE, COLLECT
from PyInstaller.building.build_main import Analysis
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# 获取项目根目录
import os.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(".")), ".."))

# 添加数据文件
datas = []

# 添加资源目录
project_root = os.path.abspath('..')
if os.path.exists(os.path.join(project_root, 'resources')):
    datas.extend([(os.path.join(project_root, 'resources'), 'resources')])

# 添加配置文件
if os.path.exists(os.path.join(project_root, 'src', 'config.py')):
    datas.append((os.path.join(project_root, 'src', 'config.py'), 'src'))
    
# 添加版本信息
version_file = os.path.join(project_root, 'version_info.py')
if os.path.exists(version_file):
    datas.append((version_file, '.'))

a = Analysis(
    [os.path.join(os.path.abspath('..'), 'main.py')],
    pathex=[os.path.abspath('..')],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt5.sip',
        'json',
        'datetime',
        'requests',
        'urllib3',
        'src',
        'src.ui',
        'src.utils',
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

pyz = PYZ(
    a.pure, 
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LoLDataCollector',
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
    icon=os.path.join(root_dir, 'resources', 'icon.ico') if os.path.exists(os.path.join(root_dir, 'resources', 'icon.ico')) else None,
)
