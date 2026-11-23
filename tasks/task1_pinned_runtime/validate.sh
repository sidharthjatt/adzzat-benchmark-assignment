#!/usr/bin/env bash
# Validate Task 1: grade the starter, the reference (5 times) and four flawed
# solutions, compare every verdict with the expected one, and write
# VALIDATION_LOG.txt. Exits non-zero if any verdict differs from what is expected.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LOG="$HERE/VALIDATION_LOG.txt"
GRADER_PY="3.12.14"  # interpreter used to run grade.py itself (grade.py is standard library only)
WORK="$(mktemp -d "${TMPDIR:-/tmp}/task1_validate.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

command -v uv >/dev/null || { echo "uv is required (brew install uv)" >&2; exit 2; }
run_py() { uv run --isolated --no-project --no-config --quiet --python "$GRADER_PY" python "$@"; }

# 1. The manifest must describe the starter exactly.
run_py "$HERE/grader/make_manifest.py" --check

# 2. Build one candidate workspace: starter plus an optional overlay folder.
build() {  # build <name> [overlay_dir]
  local ws="$WORK/$1"
  cp -R "$HERE/starter" "$ws"
  if [ -n "${2:-}" ]; then cp -R "$2/." "$ws/"; fi
  echo "$ws"
}

# 3. Grade one workspace and save its JSON report.
RESULTS="$WORK/results.tsv"
: > "$RESULTS"
grade() {  # grade <label> <expectation> <workspace>
  local report="$WORK/$1.json" code=0
  run_py "$HERE/grader/grade.py" "$3" > "$report" || code=$?
  printf '%s\t%s\t%s\t%s\n' "$1" "$2" "$code" "$report" >> "$RESULTS"
  echo "graded $1 (exit $code)"
}

grade starter        starter    "$(build starter)"
for i in 1 2 3 4 5; do
  grade "reference_run$i" reference "$(build "reference_run$i" "$HERE/reference")"
done
grade F1_modern_syntax F1 "$(build F1 "$HERE/flawed/F1_modern_syntax")"
grade F2_hardcoded     F2 "$(build F2 "$HERE/flawed/F2_hardcoded")"
grade F3_test_tamper   F3 "$(build F3 "$HERE/flawed/F3_test_tamper")"
grade F4_rounding      F4 "$(build F4 "$HERE/flawed/F4_rounding")"

# 4. Compare with expectations and write the log.
run_py - "$RESULTS" "$LOG" <<'PY'
import json, platform, subprocess, sys
from datetime import datetime, timezone

results_path, log_path = sys.argv[1], sys.argv[2]

# Required check states for each expectation. Checks not listed are not constrained,
# except that the verdict must always match.
EXPECT = {
    "starter":   ("FAIL", {"integrity": "PASS", "py3.9_visible": "FAIL", "py3.12_visible": "FAIL",
                           "py3.9_hidden": "FAIL", "py3.12_hidden": "FAIL"}),
    "reference": ("PASS", {}),
    "F1":        ("FAIL", {"integrity": "PASS", "py3.12_visible": "PASS", "py3.12_hidden": "PASS",
                           "py3.9_visible": "FAIL", "py3.9_hidden": "FAIL"}),
    "F2":        ("FAIL", {"integrity": "PASS", "py3.9_visible": "PASS", "py3.12_visible": "PASS",
                           "py3.9_hidden": "FAIL", "py3.12_hidden": "FAIL"}),
    "F3":        ("FAIL", {"integrity": "FAIL"}),
    "F4":        ("FAIL", {"integrity": "PASS", "py3.9_visible": "PASS", "py3.12_visible": "PASS",
                           "py3.9_hidden": "FAIL", "py3.12_hidden": "FAIL"}),
}
DESCRIBE = {
    "starter": "FAIL (format_duration not implemented)",
    "reference": "PASS",
    "F1": "FAIL: Python 3.12 passes, Python 3.9 fails",
    "F2": "FAIL on hidden tests",
    "F3": "FAIL on integrity check",
    "F4": "FAIL on hidden tests",
}
COLS = ["integrity", "py3.9_runtime", "py3.9_visible", "py3.9_hidden",
        "py3.12_runtime", "py3.12_visible", "py3.12_hidden"]

rows, all_ok, tools = [], True, None
for line in open(results_path):
    label, exp, code, report_path = line.rstrip("\n").split("\t")
    report = json.load(open(report_path))
    tools = tools or report["tools"]
    states = {c["name"]: c["status"] for c in report["checks"]}
    want_verdict, want_checks = EXPECT[exp]
    want_code = "0" if want_verdict == "PASS" else "1"
    ok = (report["verdict"] == want_verdict and code == want_code
          and all(states.get(k) == v for k, v in want_checks.items()))
    all_ok &= ok
    rows.append((label, DESCRIBE[exp], report["verdict"], code, [states.get(c, "-") for c in COLS],
                 "yes" if ok else "NO"))

def pytest_versions():
    out = {}
    for label, ver in tools["python"].items():
        p = subprocess.run(["uv", "run", "--isolated", "--no-project", "--no-config", "--quiet", "--python", ver,
                            "--with", tools["pytest"], "python", "-m", "pytest", "--version"],
                           capture_output=True, text=True)
        out[label] = (p.stdout + p.stderr).strip()
    return out

lines = [
    "Task 1 (pinned runtime) validation log",
    f"Run at (UTC): {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}",
    f"Host: {platform.platform()}",
    f"uv: {tools['uv']}",
    f"Python used for grading: 3.9 -> {tools['python']['3.9']}, 3.12 -> {tools['python']['3.12']} (uv-managed)",
    f"Python used to run grade.py: {platform.python_version()}",
    f"pytest pin: {tools['pytest']}",
]
for label, v in pytest_versions().items():
    lines.append(f"pytest under {label}: {v}")
lines += ["", "| Candidate | Expected | Verdict | Exit | " + " | ".join(COLS) + " | As expected |",
          "|---" * (len(COLS) + 5) + "|"]
for label, desc, verdict, code, states, ok in rows:
    lines.append(f"| {label} | {desc} | {verdict} | {code} | " + " | ".join(states) + f" | {ok} |")
ref = [r for r in rows if r[0].startswith("reference_run")]
lines += ["", f"Reference: {sum(r[2] == 'PASS' for r in ref)}/{len(ref)} runs PASS.",
          f"Overall: {'ALL VERDICTS AS EXPECTED' if all_ok else 'SOME VERDICTS DIFFER FROM EXPECTED'}"]
open(log_path, "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
sys.exit(0 if all_ok else 1)
PY
