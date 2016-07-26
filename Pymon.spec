# -*- mode: python -*-

block_cipher = None

added_files = [
         ( './Data', 'Data' ),
         ( './UI', 'UI' ),
         ( './Maps/*.tmx', 'Maps' ),
	 ( './Sprites', 'Sprites' ),
	 ( './Tilesets', 'Tilesets' ),
	 ( './Battlers', 'Battlers' ),
	 ( './EventScripts', 'EventScripts' ),
	 ( './Player', 'Player' ),
	 ( './Music', 'Music' ),
	 ( './ME', 'ME' ),
	 ( './Sounds', 'Sounds' ),
         ]

a = Analysis(['__main__.py'],
             pathex=['C:\\Users\\Matt\\Desktop\\PyGame'],
             binaries=None,
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Pymon',
          debug=False,
          strip=False,
          upx=True,
          console=False )
