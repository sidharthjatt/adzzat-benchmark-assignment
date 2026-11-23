# adzzat-benchmark-assignment

Work in progress: Adzzat Labs Head of Research, Benchmarks take-home.

## Task 1: pinned runtime

Task 1 is in `tasks/task1_pinned_runtime/`. It checks whether an agent validates code in the stated target runtime (Python 3.9) and not only in the default interpreter (Python 3.12). Reviewers should start with `TASK_CARD.md`.

To rerun the validation (needs [uv](https://github.com/astral-sh/uv); it downloads Python 3.9.25 and 3.12.14 if they are missing):

```bash
bash tasks/task1_pinned_runtime/validate.sh
```

It grades the starter, the reference solution (5 times) and four flawed solutions, writes `tasks/task1_pinned_runtime/VALIDATION_LOG.txt`, and exits 0 only if every verdict is as expected.
