# -*- mode: python ; coding: utf-8 -*-

import os
import shutil

block_cipher = None

# 获取chromium路径并准备打包数据
chromium_path = r'C:\Users\zwy\AppData\Local\ms-playwright\chromium-1234'
datas = [('river.jpg', '.')]

# 如果chromium存在，添加到打包数据
if os.path.exists(chromium_path):
    datas.append((chromium_path, 'ms-playwright'))

a = Analysis(
    ['screenshot.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['playwright', 'playwright.sync_api'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    distpath='西江水位查看分析器',  # 输出目录名称
    workpath='build',    # 工作目录名称
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='水位数据爬取',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 显示控制台，方便查看运行状态
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

