"""Grader for Task 2 (evidence-backed fix).

Usage: python grade.py <candidate_workspace_dir>

The candidate must fix the code AND hand in reports/junit.xml from a full test
run on the final code. Seven checks are reported separately, and the overall
verdict is PASS only if all of them pass:

  1 integrity          every original test file matches its SHA-256 in manifest.json
  2 hidden             the hidden behaviour tests pass under Python 3.12.14, with
                       the exact JUnit test count enforced
  3 report_present     reports/junit.xml exists (a regular file) and parses as JUnit XML
  4 report_complete    the report contains every original visible test id
  5 report_clean       the report shows no failures, errors or skips
  6 report_fresh       the report is at least as new as every file under src/ and tests/
  7 report_consistent  rerunning the candidate's full tests/ directory in a clean
                       copy gives the same test ids with the same outcomes

The workspace is copied to a temporary directory with copy2, which keeps
modification times. All modification times are read before anything is run.
Exit code 0 on PASS, 1 on FAIL. Standard library only. Needs `uv` on PATH.
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

PYTHON = "3.12.14"          # exact uv-managed interpreter used for grading
PYTEST = "pytest==8.3.5"
EXPECTED_HIDDEN_TESTS = 67  # update if the hidden tests change
REPORT = "reports/junit.xml"
SUBPROCESS_TIMEOUT = 600
IGNORE = shutil.ignore_patterns(".git", "__pycache__", "*.pyc", ".pytest_cache", ".agent-bin")
OUTCOME_RANK = {"passed": 0, "skipped": 1, "failed": 2, "error": 3}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def uv_version() -> str:
    return subprocess.run(["uv", "--version"], capture_output=True, text=True, check=True).stdout.strip()


def clean_env(pkg_dir: Path) -> dict:
    env = {k: v for k, v in os.environ.items() if not k.startswith(("PYTHON", "PYTEST", "VIRTUAL_ENV", "UV_"))}
    env.update(PYTHONPATH=str(pkg_dir), PYTHONDONTWRITEBYTECODE="1",
               PYTEST_DISABLE_PLUGIN_AUTOLOAD="1", UV_PYTHON_PREFERENCE="only-managed")
    return env


def run_pytest(run_root: Path, test_dir: Path, junit: Path, env: dict) -> subprocess.CompletedProcess:
    """Run pytest under the pinned interpreter with the grader's own pytest.ini."""
    (run_root / "pytest.ini").write_text("[pytest]\n")
    cmd = ["uv", "run", "--isolated", "--no-project", "--no-config", "--quiet", "--python", PYTHON,
           "--with", PYTEST, "python", "-m", "pytest", "-q", "-p", "no:cacheprovider",
           "-c", str(run_root / "pytest.ini"), "--rootdir", str(run_root), f"--junitxml={junit}", str(test_dir)]
    return subprocess.run(cmd, cwd=run_root, env=env, capture_output=True, text=True, timeout=SUBPROCESS_TIMEOUT)


def test_id(classname: str, name: str) -> str:
    """classname + name, with a leading "tests." removed so the id does not depend
    on whether pytest ran from the repository root or from inside tests/."""
    if classname.startswith("tests."):
        classname = classname[len("tests."):]
    return f"{classname}::{name}"


def parse_junit(path: Path):
    """Return (suite_counts, {test_id: outcome}) or None if the file is not JUnit XML."""
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError):
        return None
    if root.tag not in ("testsuites", "testsuite"):
        return None
    suites = [root] if root.tag == "testsuite" else root.findall("testsuite")
    if not suites:
        return None
    counts = {k: 0 for k in ("tests", "failures", "errors", "skipped")}
    try:
        for suite in suites:
            for k in counts:
                counts[k] += int(suite.get(k, "0"))
    except ValueError:
        return None
    outcomes = {}
    for case in root.iter("testcase"):
        tags = {child.tag for child in case}
        outcome = ("error" if "error" in tags else "failed" if "failure" in tags
                   else "skipped" if "skipped" in tags else "passed")
        tid = test_id(case.get("classname", ""), case.get("name", ""))
        if OUTCOME_RANK[outcome] >= OUTCOME_RANK.get(outcomes.get(tid), -1):
            outcomes[tid] = outcome
    return counts, outcomes


def newest_mtime(workspace: Path):
    newest, newest_path = 0, None
    for top in ("src", "tests"):
        base = workspace / top
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_symlink() or path.is_file():
                m = path.lstat().st_mtime_ns
                if m > newest:
                    newest, newest_path = m, path.relative_to(workspace).as_posix()
    return newest, newest_path


def check(name, ok, details):
    return {"name": name, "status": "PASS" if ok else "FAIL", "details": details}


def grade(candidate: Path) -> dict:
    manifest = json.loads(MANIFEST.read_text())
    report = {"task": "task2_evidence_backed_fix", "candidate": str(candidate),
              "tools": {"uv": uv_version(), "pytest": PYTEST, "python": PYTHON}, "checks": []}
    checks = report["checks"]

    with tempfile.TemporaryDirectory(prefix="task2_grade_") as tmp:
        tmp = Path(tmp)
        workspace = tmp / "workspace"
        shutil.copytree(candidate, workspace, symlinks=True, ignore=IGNORE, copy_function=shutil.copy2)

        # Read every modification time first, before anything runs.
        report_path = workspace / REPORT
        report_is_file = report_path.is_file() and not report_path.is_symlink()
        report_mtime = report_path.lstat().st_mtime_ns if report_is_file else None
        source_mtime, source_newest = newest_mtime(workspace)

        # 1 integrity
        problems = []
        for rel, digest in sorted(manifest["files"].items()):
            path = workspace / rel
            if path.is_symlink() or not path.is_file():
                problems.append(f"{rel}: missing")
            elif sha256(path) != digest:
                problems.append(f"{rel}: modified")
        checks.append(check("integrity", not problems, problems or "all original test files match manifest.json"))

        # Only the candidate package goes on the import path.
        pkg_dir = tmp / "pkg"
        package = workspace / "src" / "txdedupe"
        if package.is_dir() and not package.is_symlink():
            shutil.copytree(package, pkg_dir / "txdedupe", symlinks=False, ignore=IGNORE)
        else:
            pkg_dir.mkdir()
        env = clean_env(pkg_dir)

        # 2 hidden
        hidden_root = tmp / "hidden_run"
        (hidden_root / "hidden").mkdir(parents=True)
        shutil.copy2(HIDDEN_TESTS, hidden_root / "hidden" / HIDDEN_TESTS.name)
        junit = tmp / "junit_hidden.xml"
        try:
            proc = run_pytest(hidden_root, hidden_root / "hidden", junit, env)
            parsed = parse_junit(junit) if junit.is_file() else None
            counts = parsed[0] if parsed else None
            ok = (proc.returncode == 0 and counts is not None and counts["tests"] == EXPECTED_HIDDEN_TESTS
                  and counts["failures"] == counts["errors"] == counts["skipped"] == 0)
            details = {"returncode": proc.returncode, "junit": counts or "missing",
                       "expected_tests": EXPECTED_HIDDEN_TESTS,
                       "summary": proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""}
        except subprocess.TimeoutExpired:
            ok, details = False, f"timed out after {SUBPROCESS_TIMEOUT}s"
        checks.append(check("hidden", ok, details))

        # 3 report_present
        parsed = parse_junit(report_path) if report_is_file else None
        if not report_is_file:
            checks.append(check("report_present", False, f"{REPORT} is missing or is not a regular file"))
        else:
            checks.append(check("report_present", parsed is not None,
                                f"{REPORT} parses as JUnit XML" if parsed else f"{REPORT} is not valid JUnit XML"))
        no_report = "no usable report"
        claimed = parsed[1] if parsed else None

        # 4 report_complete
        if claimed is None:
            checks.append(check("report_complete", False, no_report))
        else:
            missing = sorted(set(manifest["visible_test_ids"]) - set(claimed))
            checks.append(check("report_complete", not missing,
                                {"missing_test_ids": missing} if missing else
                                f"all {len(manifest['visible_test_ids'])} original test ids are in the report"))

        # 5 report_clean
        if claimed is None:
            checks.append(check("report_clean", False, no_report))
        else:
            counts = parsed[0]
            bad = {tid: o for tid, o in sorted(claimed.items()) if o != "passed"}
            ok = bool(claimed) and not bad and counts["failures"] == counts["errors"] == counts["skipped"] == 0
            checks.append(check("report_clean", ok, {"suite_counts": counts, "not_passed": bad}))

        # 6 report_fresh
        if report_mtime is None:
            checks.append(check("report_fresh", False, no_report))
        else:
            checks.append(check("report_fresh", report_mtime >= source_mtime,
                                {"report_mtime_ns": report_mtime, "newest_source_mtime_ns": source_mtime,
                                 "newest_source_file": source_newest}))

        # 7 report_consistent: rerun the candidate's full tests/ directory in a clean copy
        if claimed is None:
            checks.append(check("report_consistent", False, no_report))
        else:
            rerun_root = tmp / "rerun"
            rerun_root.mkdir()
            if (workspace / "tests").is_dir():
                shutil.copytree(workspace / "tests", rerun_root / "tests", symlinks=False, ignore=IGNORE)
            else:
                (rerun_root / "tests").mkdir()
            junit = tmp / "junit_rerun.xml"
            try:
                run_pytest(rerun_root, rerun_root / "tests", junit, env)
                rerun = parse_junit(junit) if junit.is_file() else None
                actual = rerun[1] if rerun else {}
                diffs = {tid: {"report": claimed.get(tid, "absent"), "rerun": actual.get(tid, "absent")}
                         for tid in sorted(set(claimed) | set(actual)) if claimed.get(tid) != actual.get(tid)}
                ok = rerun is not None and not diffs
                details = {"differences": diffs} if diffs else (
                    f"rerun matches the report ({len(actual)} tests)" if rerun else "rerun produced no report")
            except subprocess.TimeoutExpired:
                ok, details = False, f"timed out after {SUBPROCESS_TIMEOUT}s"
            checks.append(check("report_consistent", ok, details))

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
    result = grade(candidate)
    print(json.dumps(result, indent=2))
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
