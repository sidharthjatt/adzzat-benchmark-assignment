"""Write or check grader/manifest.json from the starter repository.

Usage:
  python make_manifest.py          # write manifest.json from ../starter
  python make_manifest.py --check  # exit 1 if manifest.json does not match ../starter
"""

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STARTER = HERE.parent / "starter"


def build() -> dict:
    files = {}
    for path in sorted((STARTER / "tests").rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
            files[path.relative_to(STARTER).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    files["pyproject.toml"] = hashlib.sha256((STARTER / "pyproject.toml").read_bytes()).hexdigest()
    return {"description": "SHA-256 of every file under starter/tests/ and of starter/pyproject.toml.",
            "files": dict(sorted(files.items()))}


if __name__ == "__main__":
    manifest_path = HERE / "manifest.json"
    current = build()
    if "--check" in sys.argv:
        stored = json.loads(manifest_path.read_text())
        if stored["files"] != current["files"]:
            print("manifest.json does not match starter/", file=sys.stderr)
            sys.exit(1)
        print("manifest.json matches starter/")
    else:
        manifest_path.write_text(json.dumps(current, indent=2) + "\n")
        print(f"wrote {manifest_path}")
