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
# 获取spec文件所在目录（build目录）
spec_dir = os.path.dirname(os.path.abspath('.'))
# 项目根目录是build目录的父目录
# 但由于PyInstaller是从项目根目录运行的，所以当前目录就是根目录
if os.path.basename(os.getcwd()) == 'build':
    # 如果当前在build目录，向上一级
    root_dir = os.path.dirname(os.getcwd())
else:
    # 如果当前在项目根目录
    root_dir = os.getcwd()

# 添加数据文件
datas = []

# 添加资源目录
if os.path.exists(os.path.join(root_dir, 'resources')):
    datas.extend([(os.path.join(root_dir, 'resources'), 'resources')])

# 添加配置文件
if os.path.exists(os.path.join(root_dir, 'src', 'config.py')):
    datas.append((os.path.join(root_dir, 'src', 'config.py'), 'src'))
    
# 添加版本信息
version_file = os.path.join(root_dir, 'version_info.py')
if os.path.exists(version_file):
    datas.append((version_file, '.'))

# 添加manifest文件
manifest_file = os.path.join(root_dir, 'uac_admin.manifest')
if os.path.exists(manifest_file):
    datas.append((manifest_file, '.'))

a = Analysis(
    [os.path.join(root_dir, 'main.py')],
    pathex=[root_dir],
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
        'src.ui.main_window',
        'src.ui.monitor_tab',
        'src.ui.settings_tab',
        'src.ui.logs_tab',
        'src.utils',
        'src.utils.game_monitor',
        'src.utils.lcu_credentials',
        'src.utils.data_handler',
        'src.utils.log_manager',
        'src.utils.api_client',
        'src.utils.config_manager',
        'src.utils.log_uploader',
        'src.utils.system_utils',
        'src.config',
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
    uac_admin=True,  # 请求管理员权限
)
