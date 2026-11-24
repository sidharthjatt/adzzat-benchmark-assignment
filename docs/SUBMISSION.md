# Adzzat Labs take-home: Head of Research, Benchmarks

Candidate: Sidharth Choudhary

## One idea runs through this submission

The failure analysis found that the strongest public evidence is about agents reporting success that their current state does not support. Both tasks are built on that finding: each one checks a claim against real evidence instead of trusting it. The graders were treated the same way. Neither was trusted until it had been run against a correct solution, the unchanged starter and deliberately wrong solutions.

## Where everything is

| Assignment item | Location |
|---|---|
| Failure categories and the examples behind them | `research/failure_analysis.md` |
| Archived sources and quote checks | `research/evidence/` (`VERIFICATION.md`, `FETCH_LOG.md`) |
| Task 1: pinned runtime (category D) | `tasks/task1_pinned_runtime/` |
| Task 2: evidence-backed fix (category C) | `tasks/task2_evidence_backed_fix/` |
| How I would check difficulty | `docs/difficulty_plan.md` |
| Leakage note, the guarding check, one thing not measured, junior feedback | `docs/leakage_and_review.md` |
| Manual walkthrough of both tasks (no agent was run) | `docs/manual_walkthrough.md` |
| AI tools used | `docs/ai_tools_used.md` |
| Portfolio evidence | `docs/portfolio_evidence.md` |
| Optional stretch: a process for 100 tasks | `docs/process_100_tasks.md` |

Each task folder contains `TASK.md` (what the agent sees), `TASK_CARD.md` (for reviewers), `starter/`, `env/setup_env.sh`, `grader/`, `reference/`, `flawed/`, `validate.sh` and `VALIDATION_LOG.txt`.

## How to run

Requirements: macOS or Linux, with `uv` installed. `uv` downloads the exact Python versions used. See `README.md` for the commands that run both validations.

## What was validated, and what was not

- **Validated:** each grader against the unchanged starter (FAIL), the reference solution (PASS in 5 out of 5 runs) and deliberately wrong solutions, each failing on the checks it was designed to trigger. Each validation script also fails if its reference is replaced with a wrong solution.
- **Not done:** no coding agent was run on either task, so there are no pass rates and no difficulty estimate. `docs/difficulty_plan.md` describes how I would measure difficulty. No container image was built; the environment is defined by `env/setup_env.sh`, which was run and checked on macOS.
- **Known limits, recorded rather than hidden:** a final-state grader cannot tell whether a correct report was produced by running the tests (Task 2, candidate S6), and neither task measures the sequence of actions an agent takes. See `docs/leakage_and_review.md`.
