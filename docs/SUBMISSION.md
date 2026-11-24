# Adzzat Labs take-home: Head of Research, Benchmarks

Sidharth Choudhary

## Start here

I started by reading eight public reports of coding agents failing. The most solid evidence was about agents saying "done" or "tests pass" when their current state did not back that up. So both of my tasks check a claim against real evidence instead of trusting it.

I held the graders to the same rule. I did not trust either one until I had run it against a correct solution, the untouched starter, and several deliberately wrong solutions.

## What is where

| Assignment item | Where |
|---|---|
| Failure categories and the examples behind them | `research/failure_analysis.md` |
| Saved copies of the sources, and the quote checks | `research/evidence/` |
| Task 1: pinned runtime | `tasks/task1_pinned_runtime/` |
| Task 2: evidence-backed fix | `tasks/task2_evidence_backed_fix/` |
| How I would check difficulty | `docs/difficulty_plan.md` |
| Leakage, the main guarding check, what the tasks don't measure, feedback for the junior researcher | `docs/leakage_and_review.md` |
| Manual walkthrough of both tasks | `docs/manual_walkthrough.md` |
| AI tools I used | `docs/ai_tools_used.md` |
| Portfolio | `docs/portfolio_evidence.md` |
| Optional: a process for 100 tasks | `docs/process_100_tasks.md` |

Each task folder has the agent-facing `TASK.md`, a `TASK_CARD.md` for reviewers, the starter repo, an environment script, the grader, a reference solution, the wrong solutions, `validate.sh` and its log.

To run the checks you need macOS or Linux and `uv`, which fetches the exact Python versions. The commands are in `README.md`.

## What I checked and what I didn't

Each grader fails the untouched starter, passes the reference solution in 5 out of 5 runs, and fails every wrong solution on the check it was built to trigger. Each `validate.sh` also fails if its reference is swapped for a wrong solution. Both validations passed on my Mac and again in a fresh clone of this repo.

I did not run a coding agent on either task, so there are no pass rates and no difficulty numbers yet. `docs/difficulty_plan.md` explains how I would get them. I also did not build a container image; the environment is set up by `env/setup_env.sh`, which I ran and checked on macOS.

Two limits are written down rather than hidden. A grader that only sees the final files cannot tell whether a correct test report came from a real run (Task 2, candidate S6). And neither task measures the steps an agent took to get there.
