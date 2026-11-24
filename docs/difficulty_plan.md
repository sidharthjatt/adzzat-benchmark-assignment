# How I would check task difficulty with many runs

No coding agent was run on either task in this submission. Both graders were validated only with constructed candidate solutions (see each task's `VALIDATION_LOG.txt`). This note describes how I would measure difficulty once agent runs are available.

## 1. Make sure a failure means what it should, before measuring anything

A low pass rate only means "hard" if the task itself is sound. Before any difficulty number is read:

1. **Oracle check.** The reference solution must pass in a fresh environment every time, for example 20 out of 20 runs. Any failure means the environment or grader is flaky, and the task is fixed before going further. (Both tasks already pass 5 out of 5.)
2. **No-op check.** The unchanged starter must fail. (Both tasks already do.)
3. **Pilot triage.** On the first pilot (one small batch of runs per model), read every failed trajectory by hand and label it as one of: capability failure, task defect (ambiguous or wrong statement), environment defect (missing tool, broken install, timeout), or grader defect (correct work graded FAIL, or wrong work graded PASS). Fix every defect, give the task a new version number, and discard the pilot runs from the difficulty estimate.

## 2. The measurement itself

- **Unit of measurement:** one run is one (model, harness, task version, seed). I would use 3 to 5 models of clearly different strength, in the same harness, with at least 10 runs each.
- **Main number:** pass rate per model, reported with its denominator and a 95% Wilson interval. Never a bare percentage.
- **Consistency:** the share of runs that pass, and also whether the same model passes all k runs. A task a model passes 5 times out of 10 tells us something different from one it always passes.
- **Which check failed:** both graders report each check separately, so failures can be broken down by cause. For Task 1, the share of failures that pass on Python 3.12 but fail on 3.9 shows how often the intended failure happened, as opposed to a plain misreading of the contract. For Task 2, the failing check names which kind of unbacked claim happened: stale, narrowed, piped or inconsistent.

## 3. Is the task useful, not just hard?

- **Discrimination:** do pass rates order the models the way their known strength would predict? A task that every model passes, or every model fails, adds little information to a benchmark.
- **Ablations, to find out what makes the task hard:**
  - Task 1: state "Python 3.9" directly in `TASK.md`, and separately fix the `Makefile` to use 3.9. If the failure rate barely changes when 3.9 is stated directly, the difficulty comes from not verifying, not from not reading.
  - Task 2: run with `scripts/run_tests.sh` already fixed (no pipe), and with only one bug instead of two. This shows how much of the failure rate comes from the misleading exit code and how much from the edit-and-retest cycle.
- **Contamination:** if the tasks are ever published, compare pass rates on renamed and reworded variants. A large drop on the variants suggests memorisation.

## 4. What the numbers can and cannot show

With 10 runs, a 95% Wilson interval for an observed 5 out of 10 runs from about 24% to 76%. That is enough to separate a task at 10% from one at 70%. It is not enough to separate 40% from 55%, or to rank two similar models. To rank models finely, I would increase the number of runs on the tasks that discriminate, rather than add more tasks that every model passes.
