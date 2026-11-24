# Task card: Task 1, pinned runtime

This card is for reviewers. Agents never see it, and they never see `grader/`, `reference/`, `flawed/` or `validate.sh`. An agent receives only the contents of `starter/` and the text of `TASK.md`.

## Provenance

The task comes from case 8 in `research/failure_analysis.md` (category D: the validation runtime differs from the execution runtime). In https://github.com/openai/codex/issues/60081, an agent checked a generated PowerShell script with the parser of PowerShell 7.6.5, where the check passed. It then ran the script in Windows PowerShell 5.1, where it failed with "Unable to find type [ulong]". That report has a deterministic reproduction, which makes the mechanism the best-supported one in the sample.

This task moves the same mechanism to Python. The repository states its target runtime (Python 3.9) in `README.md`, `pyproject.toml` and the CI file. The default `python` in the environment is Python 3.12, and `make test` uses the default `python`. An agent that only runs `make test` validates in the wrong runtime.

## What it measures

Whether the agent delivers a `format_duration` that is correct under the stated target runtime (Python 3.9) and also under a newer one (Python 3.12), against a precise contract. The specific failure being probed is code that passes every check the agent ran in Python 3.12 but does not import on Python 3.9. Examples are a `match` statement, `int | None` annotations evaluated at definition time, and `zip(..., strict=True)`. All three were added in Python 3.10.

The hidden tests also check the contract in full, so a solution that is 3.9-safe but wrong still fails.

## Environment

- The agent's workspace is a copy of `starter/`.
- The default `python` on PATH is Python 3.12. Python 3.9 is also installed, reachable as `python3.9` or through `uv run --python 3.9`. TASK.md does not say this. The agent has to notice the target runtime in the repository and find the interpreter.
- No network access is needed. pytest 8.3.5 is preinstalled for both interpreters.
- **No container image was built or tested in this submission.** There is no Dockerfile. The environment above is the specification for whoever packages the task (for example, a Terminal-Bench Dockerfile).

### Setting up the environment without a container: `env/setup_env.sh`

`bash env/setup_env.sh <target_dir>` copies `starter/` into `<target_dir>` and creates `<target_dir>/.agent-bin/` with three commands:

- `python` and `python3`, which run uv's CPython 3.12.14,
- `python3.9`, which runs uv's CPython 3.9.25.

Each command is a small wrapper script that runs a virtual environment in `.agent-bin/envs/` with pytest 8.3.5 installed. The script prints the PATH line the agent harness should use. pytest ignores `.agent-bin/` because the starter sets `testpaths = ["tests"]`. The grader ignores it because only `src/durations` and the protected files are used.

Test run on 2026-11-24 (macOS arm64, uv 0.12.19). The temporary directory is shown as `<tmp>`:

```
$ bash env/setup_env.sh <tmp>/ws
Workspace ready: <tmp>/ws
PATH line for the agent harness:
export PATH="<tmp>/ws/.agent-bin:$PATH"
$ command -v python
<tmp>/ws/.agent-bin/python
$ python --version
Python 3.12.14
$ python3 --version
Python 3.12.14
$ python3.9 --version
Python 3.9.25
$ python -m pytest --version
pytest 8.3.5
$ python3.9 -m pytest --version
pytest 8.3.5
$ make test
src/durations/__init__.py:44: NotImplementedError
=========================== short test summary info ============================
FAILED tests/test_format.py::test_all_units - NotImplementedError: format_dur...
FAILED tests/test_format.py::test_zero - NotImplementedError: format_duration...
FAILED tests/test_format.py::test_largest_unit_folds_days_into_hours - NotImp...
FAILED tests/test_format.py::test_max_parts_keeps_first_component - NotImplem...
4 failed, 12 passed in 0.02s
make: *** [test] Error 1
make test exit status: 2
```

`make test` runs under 3.12.14 and fails on the starter, as expected: the four `format_duration` examples fail and the 12 `parse_duration` tests pass. As a further check, the reference solution was copied into a workspace made by this script, `.agent-bin/` included, and graded. The verdict was PASS.

Grading environment, as validated:

| Tool | Version |
|---|---|
| uv | 0.12.19 (Homebrew 2026-09-24 aarch64-apple-darwin) |
| Python 3.9 | 3.9.25 (uv-managed build) |
| Python 3.12 | 3.12.14 (uv-managed build) |
| pytest | 8.3.5 under both interpreters |
| Host | macOS 27.2.1, arm64 |

## How to run the grader

Grade one candidate workspace (a directory laid out like `starter/`):

```bash
uv run --isolated --no-project --no-config --python 3.12.14 python tasks/task1_pinned_runtime/grader/grade.py /path/to/candidate_workspace
```

It prints a JSON report and exits 0 on PASS and 1 on FAIL. The grader:

1. Copies the workspace to a temporary directory and never touches the original.
2. Checks `tests/test_format.py`, `tests/test_parse.py` and `pyproject.toml` against the SHA-256 values in `grader/manifest.json`.
3. Under Python 3.9.25 and under Python 3.12.14, each in a fresh `uv run --isolated` process with `PYTHONDONTWRITEBYTECODE=1`, does three things:
   - confirms the interpreter's exact version,
   - runs the visible tests (skipped if the integrity check failed),
   - runs the 109 hidden tests.
4. Gives PASS only if every check passes.

Rerun the whole validation, which builds the starter, the reference and the four flawed workspaces and grades each one:

```bash
bash tasks/task1_pinned_runtime/validate.sh
```

If the starter's tests or `pyproject.toml` change, regenerate the manifest with `python grader/make_manifest.py`. If the number of tests changes, update `EXPECTED_TESTS` in `grade.py`.

## Validation results

Copied from `VALIDATION_LOG.txt` (run at 2026-11-24 20:18:51 UTC):

| Candidate | Expected | Verdict | Exit | integrity | py3.9_runtime | py3.9_visible | py3.9_hidden | py3.12_runtime | py3.12_visible | py3.12_hidden | As expected |
|---|---|---|---|---|---|---|---|---|---|---|---|
| starter | FAIL (format_duration not implemented) | FAIL | 1 | PASS | PASS | FAIL | FAIL | PASS | FAIL | FAIL | yes |
| reference_run1 | PASS | PASS | 0 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | yes |
| reference_run2 | PASS | PASS | 0 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | yes |
| reference_run3 | PASS | PASS | 0 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | yes |
| reference_run4 | PASS | PASS | 0 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | yes |
| reference_run5 | PASS | PASS | 0 | PASS | PASS | PASS | PASS | PASS | PASS | PASS | yes |
| F1_modern_syntax | FAIL: Python 3.12 passes, Python 3.9 fails | FAIL | 1 | PASS | PASS | FAIL | FAIL | PASS | PASS | PASS | yes |
| F2_hardcoded | FAIL on hidden tests | FAIL | 1 | PASS | PASS | PASS | FAIL | PASS | PASS | FAIL | yes |
| F3_test_tamper | FAIL on integrity check | FAIL | 1 | FAIL | PASS | SKIPPED | FAIL | PASS | SKIPPED | FAIL | yes |
| F4_rounding | FAIL on hidden tests | FAIL | 1 | PASS | PASS | PASS | FAIL | PASS | PASS | FAIL | yes |

Reference: 5/5 runs PASS. All verdicts as expected.

Extra checks run by hand while building the task (not part of `validate.sh`):

- F1 fails on Python 3.9 with `SyntaxError` at the `match` statement. A separate variant that uses only an `int | None` annotation (no `match`) fails on 3.9 with `TypeError: unsupported operand type(s) for |` and passes on 3.12.
- A candidate that calls `os._exit(0)` at import time makes pytest exit 0. The grader still marks every test run FAIL, because there is no JUnit report.
- `validate.sh` exits 1 when the reference is replaced with the F4 rounding solution.

## Known shortcuts and the safeguard for each

| Shortcut | Safeguard |
|---|---|
| Validate only with the default `python` (3.12) and ship 3.10+ syntax | Every test also runs under Python 3.9.25 (flawed solution F1). |
| Hardcode answers for the visible examples | 109 hidden tests, including seeded random inputs (F2). |
| Edit the visible tests to match wrong behaviour | SHA-256 manifest of the visible tests. If it fails, the visible runs are skipped and counted as failures (F3). |
| Edit `pyproject.toml`, for example to add a dependency or raise `requires-python` | `pyproject.toml` is in the manifest. |
| Round instead of truncating with `max_parts` | Hidden truncation cases such as 7140 seconds with `max_parts=1` (F4). |
| Change `parse_duration` to make round trips easier | Hidden tests pin `parse_duration` on valid and invalid inputs. |
| Add `conftest.py`, pytest settings, `sitecustomize.py` or a fake `pytest` module to skip or patch tests | The grader runs tests from its own directory with its own `pytest.ini`, plugin autoload off, and only `src/durations` on `PYTHONPATH`. Other candidate files are never imported. |
| Exit the process early with status 0 | Each run must produce a JUnit report showing exactly the expected number of tests (16 visible, 109 hidden) with no failures, errors or skips. |
| Replace protected files or the package with symlinks | Protected files must be regular files. The package is copied with symlinks resolved. |

## Residual risks

- Candidate code runs in the same process as the tests. A determined solution could monkeypatch pytest or the test module at import time. The JUnit count check and the separate processes make this harder, but do not rule it out. Reading the diff of a passing solution is the remaining defence.
- The hidden tests use a fixed seed. Someone who has seen `grader/` could special-case those inputs. The seed is only a defence against agents that cannot see the grader.
- `from __future__ import annotations` makes `int | None` annotations safe on 3.9. That is a legitimate fix, not a shortcut, and it passes. A `match` statement cannot be made safe this way.
- Python 3.9 reached end of life in October 2025. Future uv releases may stop offering 3.9 builds. The pinned 3.9.25 build must stay available in the grading image.
- The visible-test check accepts extra test files that the agent adds, but does not run them. Only the protected test files and the hidden tests count.

## What it does not measure

- **Whether the agent ran Python 3.9 itself.** The grader sees only the final code. An agent that writes 3.9-safe code from habit, without ever running 3.9, passes just like one that tested carefully. An agent that tested in 3.9 but left a different bug fails. Measuring the validation behaviour itself would need the agent's command trajectory, which is category A/B territory in `failure_analysis.md`.
- Code quality, documentation, or tests the agent writes.
- Runtimes other than 3.9 and 3.12 (for example 3.10, 3.11 and 3.13).
- The PowerShell setting of the original incident. Only the mechanism is carried over.
