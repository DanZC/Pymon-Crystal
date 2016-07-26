import sys
import os

version_string = 'v0.1.1-alpha'
os.rmdir('build')
os.rename('dist/Pymon.exe','dist/Pymon-Crystal-' + version_string + '.exe')