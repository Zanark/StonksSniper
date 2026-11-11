"""Build a versioned Windows x64 executable without collecting the checkout."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import zipfile
from importlib.metadata import distribution
from pathlib import Path

from packaging.requirements import Requirement

from stonks_sniper import __version__

ROOT = Path(__file__).resolve().parents[1]


def runtime_distributions():
    pending = ["stonks-sniper"]
    seen = set()
    while pending:
        dist = distribution(pending.pop())
        name = dist.metadata["Name"].lower().replace("_", "-")
        if name in seen:
            continue
        seen.add(name)
        yield dist
        for value in dist.requires or ():
            requirement = Requirement(value)
            if requirement.marker is None or requirement.marker.evaluate({"extra": ""}):
                pending.append(requirement.name)


def release_data():
    from PyInstaller.utils.hooks import collect_data_files, copy_metadata

    data = collect_data_files("stonks_sniper")
    data += collect_data_files("tzdata")
    data += collect_data_files("certifi")
    data.append((str(ROOT / "LICENSE"), "third_party"))
    data.append((str(ROOT / "packaging" / "THIRD_PARTY_NOTICES.md"), "third_party"))
    data.append((str(ROOT / "packaging" / "SOURCES.md"), "third_party"))
    for dist in runtime_distributions():
        # Preserve metadata/licenses without editable-install direct_url.json paths.
        for source, destination in copy_metadata(dist.metadata["Name"]):
            for file in Path(source).rglob("*"):
                if file.is_file() and file.name != "direct_url.json":
                    data.append(
                        (str(file), str(Path(destination) / file.relative_to(source).parent))
                    )
        for file in dist.files or ():
            if any(
                part.lower().startswith(("license", "copying", "notice", "copyright"))
                for part in file.parts
            ):
                source = Path(dist.locate_file(file))
                if source.is_file():
                    destination = Path("third_party") / dist.metadata["Name"] / file.parent
                    data.append((str(source), str(destination)))
    python_license = Path(sys.base_prefix) / "LICENSE.txt"
    if not python_license.is_file():
        raise FileNotFoundError(f"CPython license is missing: {python_license}")
    data.append((str(python_license), str(Path("third_party") / "CPython")))
    for source, _destination in copy_metadata("pyinstaller"):
        license_file = Path(source) / "licenses" / "COPYING.txt"
        if not license_file.is_file():
            raise FileNotFoundError(f"PyInstaller license is missing: {license_file}")
        data.append((str(license_file), str(Path("third_party") / "PyInstaller")))
    return data


def build(output: Path) -> None:
    if sys.platform != "win32" or platform.machine().lower() not in {"amd64", "x86_64"}:
        raise RuntimeError("Build this Windows x64 prototype on 64-bit Windows.")
    output.mkdir(parents=True, exist_ok=False)
    subprocess.run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--distpath",
            str(output),
            "--workpath",
            str(ROOT / "build" / f"windows-{__version__}" / "pyinstaller"),
            str(ROOT / "packaging" / "windows.spec"),
        ],
        cwd=ROOT,
        check=True,
    )
    notices = output / f"StonksSniper-{__version__}-notices.zip"
    with zipfile.ZipFile(notices, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for source, destination in release_data():
            if destination.startswith("third_party") or ".dist-info" in destination:
                archive.write(source, str(Path(destination) / Path(source).name))
    inputs = [
        ROOT / "pyproject.toml",
        ROOT / "LICENSE",
        *sorted((ROOT / "src" / "stonks_sniper").glob("*.py")),
        *sorted(
            path
            for path in (ROOT / "src" / "stonks_sniper" / "assets").iterdir()
            if path.suffix in {".svg", ".txt", ".gif", ".ico"}
        ),
        ROOT / "scripts" / "build_windows.py",
        ROOT / "scripts" / "windows_entry.py",
        *sorted((ROOT / "packaging").glob("*")),
    ]
    receipt = {
        "version": __version__,
        "python": platform.python_version(),
        "architecture": platform.machine(),
        "source_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "source_dirty": bool(
            subprocess.check_output(
                ["git", "status", "--porcelain", "--untracked-files=normal"], cwd=ROOT, text=True
            ).strip()
        ),
        "dependencies": {dist.metadata["Name"]: dist.version for dist in runtime_distributions()},
        "build_tools": {
            name: distribution(name).version
            for name in (
                "pyinstaller",
                "pyinstaller-hooks-contrib",
                "setuptools",
                "packaging",
                "altgraph",
                "pefile",
                "pywin32-ctypes",
                "pip",
            )
        },
        "inputs": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in inputs
        },
        "signed": False,
    }
    (output / "build-info.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    files = sorted(path for path in output.iterdir() if path.is_file())
    (output / "SHA256SUMS.txt").write_text(
        "".join(
            f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n" for path in files
        ),
        encoding="utf-8",
    )
    print(f"Built {output.resolve()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist" / f"windows-v{__version__}")
    build(parser.parse_args().output.resolve())
