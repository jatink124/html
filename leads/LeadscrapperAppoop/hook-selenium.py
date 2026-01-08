from PyInstaller.utils.hooks import collect_submodules

# This forces PyInstaller to grab EVERY file inside selenium
hiddenimports = collect_submodules('selenium')