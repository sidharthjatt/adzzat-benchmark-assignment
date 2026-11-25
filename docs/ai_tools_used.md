# AI tools I used

The assignment allows AI tools, so here is exactly what I used and for what. I did not pay for any API, model or cloud service, and I did not run a coding agent on the two tasks.

**Claude (chat, Opus 5.5).** I used it as a research partner. It read the assignment, my earlier projects and the first draft of the failure analysis with me, checked the sources, and proposed the four failure categories, both task designs and the grading rules. I reviewed and accepted each design before it was built; the reasons are written in each task card. Claude drafted `research/failure_analysis.md` and most of the documents in `docs/`, and reviewed each Claude Code result before the next step. Claude also ran both validations on Linux x86_64 (glibc 2.39) from a fresh clone of commit 617c306, and both passed.

**Claude Code (Opus 5.5, medium effort).** It did the repository work from those specs: saving the GitHub issues, the script that checks every quote, the starters, graders, hidden tests, reference and wrong solutions, the environment and validation scripts, the manual walkthrough and the README. It ran every validation in this repo.

**ChatGPT (model not recorded).** It wrote my first planning notes and the first draft of the failure analysis. I re-checked every source from that draft against a saved copy before using it. At the end it reviewed the repo against the assignment PDF and pointed out what was still missing.

## What I did myself

- I read each of the eight source issues and checked its key facts against `research/failure_analysis.md`.
- I ran both validation scripts myself on my Mac and checked every row. Those runs are the logs now committed in the repository (run times 2026-11-25 07:05:31 and 07:05:45 UTC).
- I broke the Task 1 reference on purpose, by returning an empty string for zero, confirmed that `validate.sh` then fails, and restored the file.
- These decisions were mine: keeping the repository public, disclosing my AI use in full, skipping the optional third task, and asking ChatGPT for an independent review of the finished work.

## Checks that don't depend on trusting the tools

- A script matched every quote in the failure analysis to the saved source text, and every number in it was cross-checked against the saved copies.
- Every grader was run against the reference, the untouched starter and deliberately wrong solutions, with the expected result written down before running.

## Mistakes the tools made, and how they were caught

- The first Task 1 grader trusted pytest's exit code alone. Code that called `os._exit(0)` on import would have passed without running a single test. This was found by probing the grader, and fixed by also requiring a complete JUnit report.
- The `.gitignore` was quietly leaving both `env/setup_env.sh` scripts out of every commit. It was spotted in `git status` and fixed.
- The Task 1 task card first listed Python features that don't actually fail on 3.9. They were tested and replaced.
- One sentence in the failure analysis said more than its source (#93546) did about where fake notifications came from. I corrected it after reading the saved text.
