from pathlib import Path
import sys

from PyInstaller.utils.win32.versioninfo import (
    FixedFileInfo, StringFileInfo, StringStruct, StringTable, VarFileInfo, VarStruct, VSVersionInfo,
)

root = Path(SPECPATH).parent
sys.path.insert(0, str(root / "scripts"))
from build_windows import release_data
from stonks_sniper import __version__

version_numbers = tuple(int(part) for part in __version__.split(".")) + (0,)
version_info = VSVersionInfo(
    ffi=FixedFileInfo(filevers=version_numbers, prodvers=version_numbers, mask=0x3f,
                     flags=0, OS=0x40004, fileType=1, subtype=0, date=(0, 0)),
    kids=[
        StringFileInfo([StringTable("040904B0", [
            StringStruct("CompanyName", "Zanark"),
            StringStruct("FileDescription", "Stonks Sniper educational prototype"),
            StringStruct("FileVersion", __version__),
            StringStruct("InternalName", "StonksSniper"),
            StringStruct("OriginalFilename", f"StonksSniper-{__version__}-windows-x64.exe"),
            StringStruct("ProductName", "Stonks Sniper"),
            StringStruct("ProductVersion", __version__),
        ])]),
        VarFileInfo([VarStruct("Translation", [1033, 1200])]),
    ],
)
analysis = Analysis(
    [str(root / "scripts" / "windows_entry.py")],
    pathex=[str(root / "src")],
    binaries=[],
    datas=release_data(),
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "tkinter", "PySide6.QtWebEngineCore", "PySide6.QtWebEngineWidgets"],
    noarchive=False,
)
pyz = PYZ(analysis.pure)
exe = EXE(
    pyz, analysis.scripts, analysis.binaries, analysis.datas, [],
    name=f"StonksSniper-{__version__}-windows-x64",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    icon=str(root / "src" / "stonks_sniper" / "assets" / "logo.ico"),
    version=version_info,
)
