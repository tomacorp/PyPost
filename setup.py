from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = [], excludes = [])

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('MainWindow.py', base=base, targetName = 'pypost')
]

setup(name='PyPost',
      version = '1.0',
      description = 'Spice Post Processor',
      options = dict(build_exe = buildOptions),
      executables = executables)
