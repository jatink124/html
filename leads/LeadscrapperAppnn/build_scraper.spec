# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

# 1. Collect all Streamlit files automatically
st_datas, st_binaries, st_hiddenimports = collect_all('streamlit')

# 2. FORCE Selenium and Pandas to be included
# We manually list every part of Selenium we use
my_hiddenimports = st_hiddenimports + [
    'selenium',
    'selenium.webdriver',
    'selenium.webdriver.chrome.webdriver', # Crucial for Chrome
    'selenium.webdriver.chrome.options',
    'selenium.webdriver.common.by',
    'selenium.webdriver.common.keys',
    'selenium.webdriver.support',
    'selenium.webdriver.support.ui',
    'selenium.webdriver.support.expected_conditions',
    'selenium.webdriver.support.wait',
    'pandas'
]

# 3. Add your 'app.py' file to the package
my_datas = st_datas + [('app.py', '.')]

block_cipher = None

a = Analysis(
    ['run_app.py'],
    pathex=[],
    binaries=st_binaries,
    datas=my_datas,
    hiddenimports=my_hiddenimports,
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LeadScraper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False, # Set to True if you want to see errors in a black window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)