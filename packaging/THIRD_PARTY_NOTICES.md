# Stonks Sniper Windows prototype: third-party notices

This GPLv3, unsigned educational prototype bundles CPython, PySide6/Qt and Python
dependencies. Market observations are downloaded on request, not bundled.
Yahoo Finance is unofficial, requires internet access and may be unavailable.
No brokerage credentials, user data or API tokens are included.

The accompanying notices ZIP contains the installed distributions' license,
copyright and notice files. The same files are embedded under `third_party`
in the executable's temporary extraction directory while it runs.
`build-info.json` lists exact installed runtime/build dependency versions and
SHA-256 hashes of the allowlisted first-party build inputs.

Qt Charts is GPLv3/commercial, not LGPL. Accordingly the application is
distributed under GPL-3.0-only; the GPL text accompanies the executable.
PySide6, Shiboken and other Qt modules retain their applicable LGPL/GPL terms.
This build uses dynamically loaded Qt libraries, not a commercial Qt license.
The application source, build scripts and dependency pins are public so recipients
can rebuild with modified compatible libraries. Do not prohibit debugging or
reverse engineering of those library modifications. The single-file executable
extracts shared libraries at launch; rebuild it rather than changing that directory.
Separately licensed third-party assets and dependencies retain their own terms.

Upstream source and licensing:

- CPython: https://www.python.org/downloads/source/
- Qt: https://code.qt.io/ and https://www.qt.io/licensing/open-source-lgpl-obligations
- Qt Charts GPLv3 terms: https://doc.qt.io/qt-6/qtcharts-index.html#licenses
- PySide6/Shiboken: https://code.qt.io/cgit/pyside/pyside-setup.git/
- PyInstaller bootloader exception:
  https://pyinstaller.org/en/stable/license.html
- Other Python dependencies: project URLs in their bundled distribution metadata.
- Application/build source: https://github.com/Zanark/StonksSniper

These notices document the prototype contents; they are not a completed legal
or clean-machine qualification. Broader Windows-delivery acceptance remains open.
