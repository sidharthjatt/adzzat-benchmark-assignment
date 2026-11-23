"""Write or check grader/manifest.json from the starter repository.

The manifest holds the SHA-256 of every file under starter/tests/ and the id
(classname::name, as grade.py builds it) of every visible test. The ids are
collected by really running the starter's tests under the pinned interpreter
and reading the JUnit report.

Usage:
  python make_manifest.py          # write manifest.json from ../starter
  python make_manifest.py --check  # exit 1 if manifest.json does not match ../starter
"""

import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

from grade import IGNORE, clean_env, parse_junit, run_pytest

HERE = Path(__file__).resolve().parent
STARTER = HERE.parent / "starter"


def build() -> dict:
    files = {}
    for path in sorted((STARTER / "tests").rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
            files[path.relative_to(STARTER).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix="task2_manifest_") as tmp:
        tmp = Path(tmp)
        shutil.copytree(STARTER / "tests", tmp / "run" / "tests", ignore=IGNORE)
        shutil.copytree(STARTER / "src" / "txdedupe", tmp / "pkg" / "txdedupe", ignore=IGNORE)
        run_pytest(tmp / "run", tmp / "run" / "tests", tmp / "junit.xml", clean_env(tmp / "pkg"))
        parsed = parse_junit(tmp / "junit.xml")
    if parsed is None:
        sys.exit("could not collect the visible test ids")
    return {"description": "SHA-256 of every file under starter/tests/, and the id of every visible test.",
            "files": dict(sorted(files.items())), "visible_test_ids": sorted(parsed[1])}


if __name__ == "__main__":
    manifest_path = HERE / "manifest.json"
    current = build()
    if "--check" in sys.argv:
        stored = json.loads(manifest_path.read_text())
        if stored["files"] != current["files"] or stored["visible_test_ids"] != current["visible_test_ids"]:
            print("manifest.json does not match starter/", file=sys.stderr)
            sys.exit(1)
        print("manifest.json matches starter/")
    else:
        manifest_path.write_text(json.dumps(current, indent=2) + "\n")
        print(f"wrote {manifest_path}")
