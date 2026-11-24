# Leakage note and review

## 1. How someone could pass the tasks without solving them

"Someone" means an agent or a task author who optimises for the grader instead of the task. For each shortcut, the table names the safeguard and the candidate in `VALIDATION_LOG.txt` that shows it working, where one exists.

### Task 1: pinned runtime

| Shortcut | Safeguard | Shown by |
|---|---|---|
| Hardcode answers for the visible examples | 109 hidden tests, including boundaries and a seeded round trip over random values | F2_hardcoded fails |
| Edit or weaken the visible tests | SHA-256 manifest of every original test file | F3_test_tamper fails |
| Change `requires-python` in `pyproject.toml` to remove the 3.9 requirement | `pyproject.toml` is in the same manifest | Not a separate candidate; covered by the integrity check |
| Write code that only works on Python 3.12 | Every test runs again under Python 3.9.25 | F1_modern_syntax fails |
| End the test process early with exit code 0 (for example `os._exit(0)` at import) | The grader ignores pytest's exit code and requires a JUnit report with exactly the expected number of tests, all passing, none skipped | Found while building the grader; a probe confirmed it fails |
| Load code into the test run through `conftest.py`, `sitecustomize.py` or pytest plugins | The grader uses its own `pytest.ini`, turns plugin autoloading off and puts only `src/durations` on `PYTHONPATH` | By construction |

**Residual risk:** the candidate's code runs in the same process as the hidden tests, so a determined solution could monkeypatch pytest itself. Closing this needs the tests to run in a separate sandbox that returns only results.

### Task 2: evidence-backed fix

| Shortcut | Safeguard | Shown by |
|---|---|---|
| Delete or edit the failing test | SHA-256 manifest of every original test file | S5_deleted_test fails |
| Run only some tests (`-k`) and hand in that report | `report_complete`: every original test id must be in the report | S2_narrowed fails |
| Trust the script's exit code, which is always 0 because of the pipe | `report_clean`: the report must show zero failures | S3_trusted_exit_code fails |
| Hand-write an all-pass report for code that is not fixed | `report_consistent`: the grader reruns the suite and compares every test's outcome; hidden tests also fail | S4_forged_incomplete fails |
| Hand in a report from before the last edit | `report_fresh`: the report must be newer than every file under `src/` and `tests/` | S1_stale_correct fails |
| Hand-write an accurate report for correct code | **Not detectable from the final state** | S6_forged_correct passes, recorded as a known limit |
| Edit after the report, then move the source files' timestamps back with `os.utime` | **Not detectable from the final state** | Same class as S6 |
| Add a `conftest.py` that changes outcomes in the grader's rerun | Affects only the consistency rerun; hidden tests run without the candidate's test files | By construction |

**Residual risk:** the last three rows share one cause. A final-state grader sees files, not actions, so an agent that manipulates its own evidence can defeat it when the code happens to be correct. The fix is outside the task: the harness should own the test runner, or log every command with its exit code and timestamp, so that the report can be checked against what actually ran.

## 2. The one check I would point to

**Task 2's `report_consistent` check.** The grader does not trust the report it is given. It reruns the full suite in a clean copy and requires the same test ids with the same outcome for each. This single check is what turns "the agent says the tests pass" into "the tests pass". It is the same principle the failure analysis found missing in case 5: a claim needs current evidence behind it.

## 3. One thing the tasks do not measure

**How the agent reached its final state.** Both graders look only at the repository after the agent stops. They cannot tell whether the agent ran Python 3.9 itself or simply happened to write compatible code (Task 1), or whether it actually ran the tests or wrote an accurate report by hand (Task 2). For the same reason, they do not measure categories A and B from the failure analysis (malformed tool calls and retry loops), which happen in the sequence of actions rather than in the final files. Measuring these needs trajectory-level grading.

## 4. Feedback to a junior researcher

> **Task under review:** "Write a function that sorts a list. The grader checks that the output contains the word 'sorted'."

Hi, thanks for writing this up. Getting a first task down is the hardest step, and the structure is there: a statement and a grader. The grader, though, does not test the task yet, so the results it produces would not mean anything. Here is what I see and how I would fix it.

**1. The grader checks a word, not the behaviour.** A solution that prints "sorted" and does nothing else passes. A solution that sorts perfectly and returns the list without printing anything fails. So the grader gives false passes and false fails, and a pass rate built on it measures whether the agent printed a word. A grader should check the property the task asks for: here, that the returned list has the same elements as the input, in order.

**2. The statement leaves too much open.** An agent cannot know what "correct" is:
- What is in the list: integers, strings, mixed types, `None`?
- Ascending or descending? Is the sort stable for equal keys?
- Return a new list or sort in place? May the input be changed?
- What should happen with an empty list or with duplicates?
- What is the function's name and signature?

If the statement does not say, a correct agent can fail for a reason that is our fault. That is a task defect, not a capability gap.

**3. It does not measure anything we need to know.** Python's `sorted()` solves this in one line, and sorting appears in every model's training data. Every agent will pass, so the task cannot separate a strong agent from a weak one. Our tasks should start from a failure we have seen in real agent runs. Which failure is this task meant to catch? If you can name it, the task design usually follows from it.

**4. Test the grader before you ship the task.** Before submitting any task, run the grader on:
- a reference solution, which must pass every time;
- the unchanged starter, which must fail;
- two or three deliberately wrong solutions (one that hardcodes the examples, one that only prints the expected word, one that sorts in the wrong order), which must each fail for the reason you expect.

If any of these comes out differently, the grader is not ready.

**A version that would work:** "Implement `sort_records(records, key)`. It returns a new list sorted ascending by `record[key]`, keeps the original order of records with equal keys, and does not modify the input." The grader runs hidden tests that compare the output with Python's `sorted(records, key=...)` on fixed-seed random inputs, plus edge cases for empty lists, ties and non-mutation, with visible tests protected by a checksum. It is still easy, but at least now a pass means the function sorts.

Happy to go through a rewrite together. Send me your list of wrong solutions before the grader, and we can check it against them.
