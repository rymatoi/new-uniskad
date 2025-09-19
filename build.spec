# -*- mode: python ; coding: utf-8 -*-
import os
import shutil
import datetime
import sys
sys.setrecursionlimit(sys.getrecursionlimit() * 5)

path = os.path.join(DISTPATH)
shutil.rmtree(path)

base_name = 'Uniskad'
version = os.environ.get('UNISKAD_APP_VERSION', '3.0')
build_date = datetime.datetime.now().strftime("%Y-%m-%d")
#release = os.environ.get('IS_UNISKAD_RELSEASE', True)

icon_path = os.path.join('resources/icons', 'uniskad.ico')

name = f"{base_name}_{version}.{build_date}"
print(os.path.join(path, 'app'))

block_cipher = None


a = Analysis(['app\\start.py'],
             pathex=[os.path.join(path, 'app')],
             binaries=None,
             datas=[],
             hiddenimports=['asyncpg.pgproto.pgproto'],
             hookspath=None,
             excludes=None,
             runtime_hooks=None,
             cipher=None,
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name=name,
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          icon=icon_path,
          console=True)
dirs = [
    'config',
    'resources/docs',
    'resources/translation'
]

for d in dirs:
    dst = os.path.join(DISTPATH, d)
    print(f"Copy file '{d}' to '{dst}'")
    shutil.copytree(d, os.path.join(DISTPATH, d))

archive = shutil.make_archive(name, 'zip', DISTPATH)
print(f"Archive '{archive}' builded!")
shutil.rmtree(DISTPATH)
#shutil.rmtree(BUILDPATH)
