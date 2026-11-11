# Corresponding source for the v0.2.0 Windows prototype

The Windows application is distributed under GPL-3.0-only because Qt Charts
is GPLv3/commercial. See `LICENSE` and `THIRD_PARTY_NOTICES.md`. Third-party
components retain their own licenses.

Application, assets, build scripts and pinned requirements:
https://github.com/Zanark/StonksSniper/archive/refs/tags/v0.2.0.zip

Unmodified upstream source archives for the bundled interpreter and Qt:

- Qt 6.12.0, including Charts, Base, Declarative and SVG:
  https://download.qt.io/official_releases/qt/6.12/6.12.0/single/qt-everywhere-src-6.12.0.tar.xz
- PySide6/Shiboken 6.12.0:
  https://download.qt.io/official_releases/QtForPython/pyside6/PySide6-6.12.0-src/pyside-setup-everywhere-src-6.12.0.tar.xz
- CPython 3.13.14:
  https://www.python.org/ftp/python/3.13.14/Python-3.13.14.tar.xz
- PyInstaller bootloader 6.22.3:
  https://github.com/pyinstaller/pyinstaller/tree/v6.22.3/bootloader

These three upstream archives returned HTTP 200 when checked for this release.
No upstream source modifications were made. Exact Python dependency versions and
the public first-party input hashes are in `build-info.json`; the remaining
packages' corresponding source distributions are available at
`https://pypi.org/project/<distribution>/<version>/#files`, using the names and
versions in that receipt. The notices ZIP includes their metadata and licenses.

To rebuild or use modified compatible libraries, follow the isolated Windows
build procedure in `docs/development.md`. The dependency pins describe the
published baseline; change them intentionally for a modified rebuild.
An executable checksum is integrity evidence, not a publisher signature.
