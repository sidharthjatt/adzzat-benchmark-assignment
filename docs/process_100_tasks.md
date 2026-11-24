# Optional stretch: producing 100 tasks at steady quality

This is a one-page sketch. It is built from what was needed to make the two tasks in this submission trustworthy.

## Template

Every task is one folder with the same parts:
- `TASK.md`: the agent-facing statement, with a complete contract. Every rule the hidden tests check is written here; only the specific test values are hidden.
- `starter/`: the repository the agent receives.
- `env/setup_env.sh` (or a container image): the exact environment, with pinned interpreter and tool versions.
- `grader/`: hidden tests, a manifest of protected files and `grade.py`, which reports each check separately.
- `reference/`: a solution that passes.
- `flawed/`: at least three wrong solutions, each targeting a known shortcut.
- `validate.sh`: runs the grader on all of the above and fails if any verdict, or any set of failed checks, differs from what is expected.
- `TASK_CARD.md`: provenance (which real failure the task comes from), what it measures, what it does not, known limits.

## Pipeline

1. **Source.** Each task starts from a documented real failure in a failure log, with its evidence archived. No task without a named failure category.
2. **Author.** A researcher writes the task from the template.
3. **Automatic validation.** `validate.sh` must pass in CI: the reference passes N out of N runs, the starter fails, every flawed solution fails on its expected checks.
4. **Peer review.** A second researcher, who did not write the task, tries to pass it without solving it and gets a short time box to do so. Every working shortcut becomes a new flawed solution and a new safeguard.
5. **Pilot.** A small batch of agent runs; every failure trajectory is read and labelled (capability, task defect, environment defect, grader defect). Any defect sends the task back to step 2 with a new version number.
6. **Release.** Only tasks with zero open defects and a pilot pass rate that discriminates between models are released.

## Metrics to watch

- **Pipeline:** tasks accepted per week, and the share rejected at each stage with the reason. A rising rejection rate at peer review usually means the template or author guidance needs work.
- **Quality:** defects found after release per 100 tasks, the main quality metric. Also the share of pilot failures labelled as task or environment defects.
- **Usefulness:** the spread of pass rates across models, and the share of tasks that every model passes or every model fails.
- **Coverage:** number of tasks per failure category, so the benchmark does not drift towards whatever is easiest to write.

## Main risks

- **Grader drift:** authors copy a grader pattern without its safeguards. A shared grader library and `validate.sh` in CI reduce this.
- **Leakage:** tasks or hidden tests reach training data. Hidden tests stay private, values are rotated by seed, and renamed variants are compared periodically.
- **Reviewer fatigue:** peer review becomes a rubber stamp. Track how many shortcuts each reviewer finds, and rotate reviewers.
