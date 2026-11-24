# AI tools used

The assignment allows AI tools and asks which were used and how. No paid API, model or cloud service was bought or called for this work; the tools below were used through subscriptions I already had. No coding agent was run on the two tasks.

| Tool | What it contributed |
|---|---|
| Claude (chat, Claude Opus 5.5) | Read the assignment, my earlier projects and the first failure-analysis draft. Checked the draft's sources, proposed the four failure categories, both task designs and the grading policies recorded in each `TASK_CARD.md`, and wrote the specification for each Claude Code step. Drafted `research/failure_analysis.md` and the documents in `docs/` except `manual_walkthrough.md`. Reviewed every Claude Code output before the next step. |
| Claude Code (Claude Opus 5.5, medium effort setting) | All repository work: archiving the GitHub issues through the public GitHub API, the script-checked quote table, the starters, graders, hidden tests, reference and flawed solutions, environment scripts, validation scripts, `docs/manual_walkthrough.md` and the README. It ran every validation reported in this repository. |
| ChatGPT (model/version not recorded) | Wrote the initial planning brief and the first draft of the failure analysis. Every source in that draft was re-checked against an archived copy before use. Near the end, it reviewed the repository against the assignment PDF and flagged missing items: the documents were not yet merged into the repository, placeholders remained, the README still said "work in progress", and a manual walkthrough was missing. |

## How the work was split

Claude proposed the task designs and grading policies. I reviewed and accepted each one before it was built, and the reasoning for each is written in the task cards so it can be checked. Claude Code wrote the code from those specifications.

## Checks that do not rely on trusting the AI tools

- Every quoted claim in the failure analysis was matched to archived source text by a script, and every number in it was cross-checked against the archive.
- Every grader was run against a reference solution, the unchanged starter and deliberately wrong solutions, with the expected verdicts and the expected failing checks written down before running.

## Mistakes the tools made, and how they were caught

- Claude Code's first Task 1 grader trusted pytest's exit code. Code that called `os._exit(0)` at import would have passed without running any test. Claude Code found this while probing its own grader and closed it by requiring a complete JUnit report.
- The repository's `.gitignore` silently excluded both `env/setup_env.sh` scripts from commits. Claude Code noticed this in `git status` and fixed it.
- Task 1's task card first gave examples of Python features that do not actually fail on Python 3.9. Claude Code checked them and replaced them.
- One sentence of the failure analysis claimed more than its source (#93546) said about where forged notifications came from. It was corrected after the archived text was reviewed.
