# adzzat-benchmark-assignment

Take-home for Adzzat Labs, Head of Research, Benchmarks: a failure analysis of public coding-agent issues, and two benchmark tasks built from it.
Task 1 checks whether an agent validates code in the stated target runtime. Task 2 checks whether its test report is current, complete and true for its final code.
Each task has a grader validated against a reference solution, the unchanged starter and deliberately wrong solutions.

**Reviewers: start with [`docs/SUBMISSION.md`](docs/SUBMISSION.md).**

## What was not done

- No coding agent was run on either task.
- No agent pass rate was measured, so there is no difficulty estimate. `docs/difficulty_plan.md` describes how it would be measured.
- No container image was built. Each task's environment is defined by its `env/setup_env.sh`, which was run and checked on macOS.

## Repository structure

```
README.md
docs/
  SUBMISSION.md              starting point for reviewers
  manual_walkthrough.md      both tasks followed by hand (no agent run)
  difficulty_plan.md         how difficulty would be measured
  leakage_and_review.md      shortcuts, safeguards, limits, junior feedback
  ai_tools_used.md
  process_100_tasks.md       optional stretch
research/
  failure_analysis.md        eight cases, four failure categories
  evidence/                  archived GitHub issues, FETCH_LOG.md, VERIFICATION.md
tasks/
  task1_pinned_runtime/      category D: validation runtime differs from execution runtime
  task2_evidence_backed_fix/ category C: claims not grounded in current evidence
```

Each task folder contains:

- `TASK.md`: what the agent sees;
- `TASK_CARD.md`: for reviewers;
- `starter/`, `env/setup_env.sh`, `grader/`, `reference/` and `flawed/`;
- `validate.sh` and `VALIDATION_LOG.txt`.

## Running the validations

Checked on macOS (Apple Silicon) and on Linux x86_64 (glibc 2.39), each from a fresh clone. The scripts need bash. On Windows, use WSL 2 with Ubuntu; native Windows was not tested. No paid API is used.

1. Install uv 0.12.19 or newer.
   - macOS: `brew install uv`
   - Linux or WSL: `curl -LsSf https://astral.sh/uv/install.sh | sh`, then open a new terminal.

   Check the version with `uv --version`. If it is older than 0.12.19, update it first (`brew upgrade uv`, or `uv self update` if you used the install script). An older uv may not be able to download the pinned Python versions.

2. Clone the repository and go into it:

   ```bash
   git clone https://github.com/sidharthjatt/adzzat-benchmark-assignment.git
   cd adzzat-benchmark-assignment
   ```

3. Run both validations from the repository root. The first run needs internet access, because uv downloads CPython 3.9.25, CPython 3.12.14 and pytest 8.3.5.

   ```bash
   bash tasks/task1_pinned_runtime/validate.sh
   bash tasks/task2_evidence_backed_fix/validate.sh
   ```

Each script grades the unchanged starter, the reference solution (5 times) and the flawed candidates, prints the results table and writes it to the task's `VALIDATION_LOG.txt`. It exits 0 only if every result is as expected. The last line is `Overall: ALL VERDICTS AS EXPECTED` for Task 1 and `Overall: ALL VERDICTS AND FAILED CHECKS AS EXPECTED` for Task 2. Because the log is rewritten with the new run time, `git status` will show it as modified.

## Recorded results

These results are taken from the `VALIDATION_LOG.txt` files in this repository.

- **Task 1.** The starter FAILs. The reference PASSes in 5 out of 5 runs. Every flawed candidate FAILs on the check it targets:
  - F1_modern_syntax fails only under Python 3.9;
  - F2_hardcoded and F4_rounding fail the hidden tests;
  - F3_test_tamper fails the integrity check.
- **Task 2.** The starter FAILs. The reference PASSes in 5 out of 5 runs. S1 to S5 each FAIL with exactly the expected set of failed checks. S6_forged_correct (correct code with a hand-written accurate report) PASSes. It is recorded as a known limit: a grader that sees only the final state cannot detect it.
