# adzzat-benchmark-assignment

Work in progress: Adzzat Labs Head of Research, Benchmarks take-home.

## Running the validations

Both tasks need [uv](https://github.com/astral-sh/uv). uv downloads the pinned interpreters (CPython 3.9.25 and 3.12.14) and pytest 8.3.5 if they are missing. No paid APIs are used. Each command grades the starter, the reference solution (5 times) and the flawed candidates, writes the task's `VALIDATION_LOG.txt`, and exits 0 only if every result is as expected.

```bash
bash tasks/task1_pinned_runtime/validate.sh
```

```bash
bash tasks/task2_evidence_backed_fix/validate.sh
```

Each task also has `env/setup_env.sh <target_dir>`, which makes an agent workspace with the right interpreters on PATH. No container image was built or tested.

## Task 1: pinned runtime

Task 1 is in `tasks/task1_pinned_runtime/`. It checks whether an agent validates code in the stated target runtime (Python 3.9) and not only in the default interpreter (Python 3.12). It is built on category D in `research/failure_analysis.md`. Reviewers should start with `TASK_CARD.md`.

## Task 2: evidence-backed fix

Task 2 is in `tasks/task2_evidence_backed_fix/`. The agent fixes two bugs in a transaction-deduplication library and hands in a JUnit report from a full test run on its final code. The grader checks the code with hidden tests, and checks that the report is complete, clean, fresh and consistent with a rerun. The repository's own test script loses pytest's exit status through a pipe. The task is built on category C in `research/failure_analysis.md`. Reviewers should start with `TASK_CARD.md`.
