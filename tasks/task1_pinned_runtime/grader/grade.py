"""Grader for Task 1 (pinned runtime).

Usage: python grade.py <candidate_workspace_dir>

Steps:
  1. Copy the candidate workspace to a temporary directory. The original is never touched.
  2. Integrity: check every file listed in manifest.json (the visible tests and
     pyproject.toml) against its SHA-256.
  3. Under Python 3.9 and under Python 3.12, each in a fresh process:
       - confirm the interpreter's exact version,
       - run the visible tests (skipped if the integrity check failed),
       - run the hidden tests.
     Only the candidate's src/durations package is put on PYTHONPATH. The
     candidate's pytest configuration, conftest files and other files are not used.
  4. Print a JSON report. The overall verdict is PASS only if every check passes.
     Exit code 0 on PASS, 1 on FAIL.

Standard library only. Needs `uv` on PATH.
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "manifest.json"
HIDDEN_TESTS = HERE / "hidden_tests" / "test_hidden.py"

# Exact interpreter versions used for grading (uv-managed builds).
RUNTIMES = {"3.9": "3.9.25", "3.12": "3.12.14"}
PYTEST = "pytest==8.3.5"
SUBPROCESS_TIMEOUT = 600

# Exact number of test cases each suite must report as passed. A run only
# passes if pytest exits 0 AND its JUnit XML report shows exactly this many
# tests with no failures, errors or skips. This stops candidate code that
# exits the process early (for example os._exit(0) at import time) from
# looking like a pass. Update these if the tests change.
EXPECTED_TESTS = {"visible": 16, "hidden": 109}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def uv_version() -> str:
    out = subprocess.run(["uv", "--version"], capture_output=True, text=True, check=True)
    return out.stdout.strip()


def clean_env(pkg_dir: Path) -> dict:
    env = {k: v for k, v in os.environ.items() if not k.startswith(("PYTHON", "PYTEST", "VIRTUAL_ENV", "UV_"))}
    env.update(
        PYTHONPATH=str(pkg_dir),
        PYTHONDONTWRITEBYTECODE="1",
        PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
        UV_PYTHON_PREFERENCE="only-managed",
    )
    return env


def uv_run(version: str, args: list, cwd: Path, env: dict, with_pytest: bool) -> subprocess.CompletedProcess:
    cmd = ["uv", "run", "--isolated", "--no-project", "--no-config", "--quiet", "--python", version]
    if with_pytest:
        cmd += ["--with", PYTEST]
    cmd += ["python"] + args
    return subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=SUBPROCESS_TIMEOUT)


def tail(text: str, lines: int = 25) -> str:
    return "\n".join(text.strip().splitlines()[-lines:])


def check_integrity(workspace: Path, manifest: dict) -> dict:
    problems = []
    for rel, digest in sorted(manifest["files"].items()):
        path = workspace / rel
        if path.is_symlink() or not path.is_file():
            problems.append(f"{rel}: missing")
        elif sha256(path) != digest:
            problems.append(f"{rel}: modified")
    return {
        "name": "integrity",
        "status": "PASS" if not problems else "FAIL",
        "details": "all protected files match manifest.json" if not problems else problems,
    }


def read_junit(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return {}
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    if suite is None:
        return {}
    return {k: int(suite.get(k, "0")) for k in ("tests", "failures", "errors", "skipped")}


def run_pytest(version: str, suite: str, test_dir: Path, run_root: Path, env: dict, junit: Path) -> dict:
    args = ["-m", "pytest", "-q", "-p", "no:cacheprovider", "-c", str(run_root / "pytest.ini"),
            "--rootdir", str(run_root), f"--junitxml={junit}", str(test_dir)]
    try:
        proc = uv_run(version, args, cwd=run_root, env=env, with_pytest=True)
    except subprocess.TimeoutExpired:
        return {"status": "FAIL", "details": f"timed out after {SUBPROCESS_TIMEOUT}s"}
    summary = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""
    counts = read_junit(junit)
    expected = EXPECTED_TESTS[suite]
    counts_ok = (counts.get("tests") == expected and counts.get("failures") == 0
                 and counts.get("errors") == 0 and counts.get("skipped") == 0)
    passed = proc.returncode == 0 and counts_ok
    result = {"status": "PASS" if passed else "FAIL", "returncode": proc.returncode, "summary": summary,
              "junit": counts or "missing", "expected_tests": expected}
    if not passed:
        result["output_tail"] = tail(proc.stdout + "\n" + proc.stderr)
    return result


def grade(candidate: Path) -> dict:
    manifest = json.loads(MANIFEST.read_text())
    report = {"task": "task1_pinned_runtime", "candidate": str(candidate),
              "tools": {"uv": uv_version(), "pytest": PYTEST, "python": dict(RUNTIMES)}, "checks": []}
    checks = report["checks"]

    with tempfile.TemporaryDirectory(prefix="task1_grade_") as tmp:
        tmp = Path(tmp)
        workspace = tmp / "workspace"
        shutil.copytree(candidate, workspace, symlinks=True,
                        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", ".pytest_cache"))

        integrity = check_integrity(workspace, manifest)
        checks.append(integrity)

        # Only the candidate package goes on the import path.
        package = workspace / "src" / "durations"
        pkg_dir = tmp / "pkg"
        if package.is_dir() and not package.is_symlink():
            shutil.copytree(package, pkg_dir / "durations", symlinks=False)
        else:
            pkg_dir.mkdir()
        checks.append({"name": "package_present",
                       "status": "PASS" if (pkg_dir / "durations" / "__init__.py").is_file() else "FAIL",
                       "details": "src/durations/__init__.py"})

        run_root = tmp / "run"
        (run_root / "visible").mkdir(parents=True)
        (run_root / "hidden").mkdir()
        (run_root / "pytest.ini").write_text("[pytest]\n")
        for rel in manifest["files"]:
            if rel.startswith("tests/") and (workspace / rel).is_file():
                shutil.copy2(workspace / rel, run_root / "visible" / Path(rel).name)
        shutil.copy2(HIDDEN_TESTS, run_root / "hidden" / HIDDEN_TESTS.name)

        env = clean_env(pkg_dir)
        for label, version in RUNTIMES.items():
            probe = uv_run(version, ["-c", "import platform; print(platform.python_version())"],
                           cwd=run_root, env=env, with_pytest=False)
            actual = probe.stdout.strip()
            checks.append({"name": f"py{label}_runtime", "status": "PASS" if actual == version else "FAIL",
                           "details": f"expected {version}, got {actual or probe.stderr.strip()}"})

            if integrity["status"] == "PASS":
                visible = run_pytest(version, "visible", run_root / "visible", run_root, env,
                                     tmp / f"junit_{label}_visible.xml")
            else:
                visible = {"status": "SKIPPED", "details": "integrity check failed, so the visible tests cannot be trusted"}
            checks.append({"name": f"py{label}_visible", **visible})
            hidden = run_pytest(version, "hidden", run_root / "hidden", run_root, env, tmp / f"junit_{label}_hidden.xml")
            checks.append({"name": f"py{label}_hidden", **hidden})

    report["verdict"] = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
    return report


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python grade.py <candidate_workspace_dir>", file=sys.stderr)
        return 2
    candidate = Path(sys.argv[1]).resolve()
    if not candidate.is_dir():
        print(f"not a directory: {candidate}", file=sys.stderr)
        return 2
    report = grade(candidate)
    print(json.dumps(report, indent=2))
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
