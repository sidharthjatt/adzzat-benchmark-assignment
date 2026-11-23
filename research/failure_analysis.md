# Part 1: Failure Analysis of Coding-Agent Attempts

Sources accessed: 23 November 2026. Every source is a public GitHub issue. The issue text used here is archived unchanged in `research/evidence/`, and `research/evidence/VERIFICATION.md` checks each factual claim below against an exact quote from that archive.

## 1. Method and its limits

I reviewed eight publicly reported failed or flawed coding-agent attempts across four agent harnesses: Codex, OpenCode, OpenHands and Claude Code. I did not run these agents myself. I did not reproduce any of the failures. All evidence is what the reporters published.

For each case I recorded the agent, the version, the model, what the agent did, what the tool or environment returned, the outcome, and the type of evidence available. I graded evidence quality as follows:

- **Strong**: the report quotes session records (JSONL or logs) or gives counts measured against them, or gives a minimal deterministic reproduction.
- **Medium**: the report gives versions and a step-by-step description, but no raw record.
- **Weak**: a single log line with no task context and no outcome.

The selection is deliberately diverse rather than representative. I chose cases that show distinct failure patterns. Section 5 explains what this means for the conclusions.

## 2. The eight cases

### Case 1: Codex emits a lone `{` as tool-call arguments
- **Source**: https://github.com/openai/codex/issues/29549 (open)
- **Agent and model**: Codex Desktop App v0.142.0-alpha.6; a custom model named "beast" served through vLLM.
- **What happened**: the model emitted a function call whose `arguments` value was only `{`, so the call could not be parsed or executed. It happened twice, in two sessions on one day.
- **Evidence**: strong for the event itself, because the report body contains log excerpts. The user's task and the full surrounding session are not included.
- **Note**: a separate Codex issue (https://github.com/openai/codex/issues/19765) describes the same symptom with weaker models: truncated JSON in tool arguments, with the model often failing to repair the call after receiving the parse error.

### Case 2: OpenCode repeats an edit using text that is not in the file
- **Source**: https://github.com/anomalyco/opencode/issues/21850 (closed)
- **Agent and model**: OpenCode 1.3.14, 1.3.17, 1.4.0 and 1.4.3; gemma4-31b served locally through vLLM. The task was a syntax fix in a Rust file.
- **What happened**: the agent read the file, then called the edit tool with an `oldString` that differed from what the read had returned. The tool replied "Could not find oldString in the file." The agent repeated the same incorrect call more than ten times.
- **Evidence**: medium. The reporter describes the steps; no raw session log is included.

### Case 3: OpenHands calls a tool that does not exist
- **Source**: https://github.com/OpenHands/OpenHands/issues/8805 (closed as not planned after going stale; originally filed under All-Hands-AI/OpenHands)
- **Agent and model**: OpenHands 0.39 on macOS; Devstral.
- **What happened**: the agent called `execute_code`. The environment returned an error that listed the tools actually available, including `execute_bash` and `execute_ipython_cell`.
- **Evidence**: weak. One log line. The task, the rest of the session and whether the agent recovered are all unknown.

### Case 4: Claude Code writes Bash calls as plain text, so they never run
- **Source**: https://github.com/anthropics/claude-code/issues/63870 (open)
- **Agent and model**: Claude Code 2.1.156 and 2.1.158 on macOS; an Opus model; a long repository workflow.
- **What happened**: in one session, the reporter's analysis of the session JSONL found 347 normal structured Bash tool calls and 23 intended Bash calls written as ordinary text instead. Text is not executed, so those 23 commands never ran. Later turns in the same session confirm that a commit, a push, a pull request and a merge described in the conversation had not happened.
- **Evidence**: strong. The report gives counts measured against the session file, a representative (shortened) JSONL record and a per-turn table.
- **Note**: a commenter on the issue reports a similar symptom caused by an organisation permission setting that denied all tool calls. The same symptom can therefore have an environment cause.

### Case 5: Claude Code reports "all tests pass" from a stale or piped test run
- **Source**: https://github.com/anthropics/claude-code/issues/104504 (open)
- **Agent and model**: Claude Code 2.1.304, across 150 sessions from one team.
- **What happened**: the reporters labelled 357 claims that tests passed against the session JSONL (commands, exit codes, file edits, timestamps). In their development set, 32 of the 36 claims with no up-to-date supporting run were stale: tests had passed earlier, the agent edited code again, and it then reported the old pass as current. The report also describes claims based on piped output, where the exit status of the test command was lost.
- **Evidence**: strong. This is the only case with a labelled sample. It is still one team's sessions and one team's labels, not an independent study.

### Case 6: Claude Code writes fake system notifications and reports results from them
- **Source**: https://github.com/anthropics/claude-code/issues/105340 (open)
- **Agent and model**: Claude Code 2.1.304; Claude Opus 5.5.
- **What happened**: the agent started a background job, then wrote in its own output a task-completion notification with an invented tool-call ID saying the job had finished with exit code 0. It also wrote two fake monitor events for a script that was still running, and reported results based on them.
- **Evidence**: medium-strong. The report describes the session records but does not quote them.
- **Note**: other public Claude Code issues report the opposite direction. Issues #79250 and #87519 describe the harness's own notification channel delivering events that did not happen. Issue #93546 describes forged completion notifications reaching the model's context from a source the reporter could not identify; there, the model caught them by checking the disk directly. Both directions are reported publicly.

### Case 7: OpenCode repeats an invalid skill name about 22 times
- **Source**: https://github.com/anomalyco/opencode/issues/61198 (closed)
- **Agent and model**: OpenCode 2.2.5; ollama/lfm3-omni:2b, a 2-billion-parameter local model.
- **What happened**: asked which skills were available, the agent tried to load a skill named `general`, which is the name of an agent type, not a skill. The valid skill names were available to it. The tool returned "Unable to load skill general". The agent repeated the identical failing call about 22 times and never recovered.
- **Evidence**: medium. Version, model and steps are given. The reporter names a session export, but no link to it is in the issue body, so I could not review it.
- **Note**: the issue's title frames part of the problem as the harness having no fallback: nothing stops a model that keeps sending the same failing call.

### Case 8: Codex checks a PowerShell script in one version and runs it in another
- **Source**: https://github.com/openai/codex/issues/60081 (open)
- **Agent and model**: Codex Desktop on Windows. The original Codex build and model are not established; the report says so itself. The report also states that it was prepared with AI assistance.
- **What happened**: a generated script used the `[ulong]` type. The agent checked the script with PowerShell's syntax parser in PowerShell 7.6.5, where the check passed, then launched it explicitly in Windows PowerShell 5.1, where it failed with "Unable to find type [ulong]".
- **Evidence**: strong for the mechanism. The report gives a minimal reproduction with exact interpreter versions, and the behaviour is deterministic. Weak for attribution to a specific model.

## 3. Failure categories

| Category | Cases | What goes wrong |
|---|---|---|
| A. Tool-call protocol adherence | 1, 3, 4 | The agent's action never reaches the tool in a valid form: malformed arguments, a tool that does not exist, or a call written as text. |
| B. Recovery after a deterministic error | 2, 7 | The tool returns a clear error and the agent sends the same failing call again instead of changing its input or stopping. |
| C. Claims not grounded in current evidence | 5, 6, and the downstream effect of 4 | The agent reports success that the latest state does not support: an old test pass, an invented notification, or work it described but never executed. |
| D. Validation runtime differs from execution runtime | 8 | The agent validates in one environment and runs in another, so the validation does not prove what it appears to prove. |

## 4. Capability gaps or task and environment defects?

The same symptom can come from the model, from the harness around it, or from the environment. I classify each case by what its evidence can support.

**More consistent with a capability gap**
- **Case 2**: the error message was correct and explicit, and the correct text was already in the agent's context. One caveat: in OpenCode the same error message can also be caused by an environment problem (issue #33068 reports invalid UTF-8 bytes making a correct `oldString` fail to match). In this case the reporter shows that the model's string differed from what it had read, so the model is the likelier cause.
- **Case 5**: the test runner behaved correctly; the agent's claim did not match its own record.
- **Case 3**: the list of valid tools was available, and the agent chose one outside it. This is weakly supported because only one log line exists.

**Mixed: model and harness or environment both contribute**
- **Case 1**: malformed output came from the model as served through vLLM. Model generation, serving and streaming cannot be separated from the report.
- **Case 4**: the model produced text instead of a structured call, but the harness accepted that text as an ordinary reply without flagging it. A permission setting can cause the same symptom.
- **Case 7**: a very small local model made the first error, and the harness had no guard against identical repeated calls.
- **Case 8**: the two PowerShell versions genuinely differ, which is an environment fact. Choosing to validate in a different interpreter from the one used to run is the agent's planning error.

**Ambiguous**
- **Case 6**: this report attributes the fake notifications to the model's own output. Other public reports describe the harness itself delivering fake notifications. Without the session files, I cannot rule out either.

No case is a pure task defect, because these are real user sessions rather than benchmark tasks. The environment defects I found (an error message that can be triggered by file encoding, a missing retry guard, a notification channel that has been reported to deliver false events) are exactly the kind of defect a benchmark task must remove before its failures can be read as capability gaps.

## 5. What this sample cannot show

1. **No failure rate.** Eight hand-picked reports say nothing about how often any agent fails.
2. **No ranking.** The cases come from different harnesses, models, versions and operating systems. They cannot rank Codex, OpenCode, OpenHands and Claude Code against each other.
3. **No prevalence of any category.** Bug reports are filed when something goes visibly wrong, and dramatic failures are more likely to be reported. The categories are what I found, not how common each is.
4. **Limited causal attribution.** Except for case 8's deterministic mechanism, I could not separate model, harness and environment causes without the full session files and a controlled reproduction.
5. **No independent verification.** I checked that each claim appears in the published report. I did not reproduce any failure, and I could not review attached session files.
6. **No generalisation across models.** Cases 2 and 7 involve small local models; case 5 and 6 involve one frontier model family. Whether larger or newer models show the same behaviour cannot be concluded from this sample.

## 6. From categories to tasks

Categories C and D can be tested by grading the final state of a repository, which makes them suitable for objective tasks. Task 1 is built on category D and Task 2 on category C.

Categories A and B depend on the sequence of tool calls rather than the final state. Measuring them properly needs the harness to record and expose the full trajectory, for example counting identical consecutive failed calls. That is outside what a final-state grader can see, and the tasks in this submission do not measure them.
