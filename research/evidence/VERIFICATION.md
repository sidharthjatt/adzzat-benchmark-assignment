# Verification of Part 1 sources

Access date for every source: 2026-11-23.

This file records only what the saved issue text says. It does not judge whether a report is correct.

How it was checked:

- Each issue was saved as JSON in this folder. See `FETCH_LOG.md` for how it was fetched (the GitHub REST API, because the `gh` CLI was not installed).
- "FOUND" means the saved JSON states the claim. "NOT FOUND" means it does not.
- Each quote was checked by a script to be an exact copy of text in the saved JSON, and to be at most 20 words. The cell says whether it comes from the issue body or a comment.
- State and created date come from the saved JSON. "Created" is the UTC date.
- `All-Hands-AI/OpenHands` now redirects to `OpenHands/OpenHands`. The file keeps the requested name, `All-Hands-AI_OpenHands_8805.json`.

| Issue URL | Title | State | Created | Accessed | Claim checked | Result | Supporting quote (verbatim, at most 20 words; where it appears) | Contains raw log/JSONL excerpt in body? |
|---|---|---|---|---|---|---|---|---|
| https://github.com/openai/codex/issues/29549 | Bug Report: Codex App — LLM Returns Invalid JSON in Function Call Arguments | OPEN | 2026-06-23 | 2026-11-23 | Tool-call arguments value was only "{" | FOUND | "arguments: "{" — a lone opening brace with no content." (body) | yes |
| https://github.com/openai/codex/issues/29549 | Bug Report: Codex App — LLM Returns Invalid JSON in Function Call Arguments | OPEN | 2026-06-23 | 2026-11-23 | Same pattern appeared in two sessions | FOUND | "It occurred twice across two sessions in one day of usage." (body) | yes |
| https://github.com/openai/codex/issues/29549 | Bug Report: Codex App — LLM Returns Invalid JSON in Function Call Arguments | OPEN | 2026-06-23 | 2026-11-23 | Codex Desktop version | FOUND | "App: Codex Desktop App v0.142.0-alpha.6" (body) | yes |
| https://github.com/openai/codex/issues/29549 | Bug Report: Codex App — LLM Returns Invalid JSON in Function Call Arguments | OPEN | 2026-06-23 | 2026-11-23 | Model served through vLLM | FOUND | "the "beast" model (served via vLLM) returns invalid JSON" (body) | yes |
| https://github.com/openai/codex/issues/19765 | tool calls sometimes fail because the model emits truncated JSON in `function_call.arguments` | OPEN | 2026-04-27 | 2026-11-23 | (no claims listed for this issue) | n/a | — | no (1) |
| https://github.com/openai/codex/issues/60081 | Windows: generated PowerShell scripts pass AST validation but fail in explicitly selected PowerShell 5.1 | OPEN | 2026-11-07 | 2026-11-23 | PowerShell 7.6.5 | FOUND | "Control process: PowerShell 7.6.5, Core edition." (body) | no (2) |
| https://github.com/openai/codex/issues/60081 | Windows: generated PowerShell scripts pass AST validation but fail in explicitly selected PowerShell 5.1 | OPEN | 2026-11-07 | 2026-11-23 | Windows PowerShell 5.1 | FOUND | "Explicitly selected child: Windows PowerShell 5.1.26100.9711, Desktop edition." (body) | no (2) |
| https://github.com/openai/codex/issues/60081 | Windows: generated PowerShell scripts pass AST validation but fail in explicitly selected PowerShell 5.1 | OPEN | 2026-11-07 | 2026-11-23 | [ulong] | FOUND | "Unable to find type [ulong]." (body) | no (2) |
| https://github.com/openai/codex/issues/60081 | Windows: generated PowerShell scripts pass AST validation but fail in explicitly selected PowerShell 5.1 | OPEN | 2026-11-07 | 2026-11-23 | Generating model or Codex build is stated | NOT FOUND (3) | "The original Codex desktop build and original generating model were not independently established from the retained records." (body) | no (2) |
| https://github.com/anomalyco/opencode/issues/21850 | Bug Model enters infinite loop due to hallucinated oldString in edit tool calls | CLOSED | 2026-04-10 | 2026-11-23 | Same incorrect edit repeated "10+" times | FOUND | "repeats the exact same incorrect edit call multiple times (10+ times)" (body) | no |
| https://github.com/anomalyco/opencode/issues/21850 | Bug Model enters infinite loop due to hallucinated oldString in edit tool calls | CLOSED | 2026-04-10 | 2026-11-23 | OpenCode versions | FOUND | "1.3.14, 1.3.17, 1.4.0, 1.4.3" (body; listed under the form heading "OpenCode version") | no |
| https://github.com/anomalyco/opencode/issues/21850 | Bug Model enters infinite loop due to hallucinated oldString in edit tool calls | CLOSED | 2026-04-10 | 2026-11-23 | Model gemma4-31b | FOUND | "Model: gemma4-31b (local-vllm/gemma4-31b)" (body) | no |
| https://github.com/anomalyco/opencode/issues/61198 | agent: skill tool loops on invalid id instead of falling back | CLOSED | 2026-11-02 | 2026-11-23 | About 22 repeated calls | FOUND | "the agent re-issues the identical failing call ~22 times in a row, never recovering." (body) | no (4) |
| https://github.com/anomalyco/opencode/issues/61198 | agent: skill tool loops on invalid id instead of falling back | CLOSED | 2026-11-02 | 2026-11-23 | opencode 2.2.5 | FOUND | "opencode version: 2.2.5" (body) | no (4) |
| https://github.com/anomalyco/opencode/issues/61198 | agent: skill tool loops on invalid id instead of falling back | CLOSED | 2026-11-02 | 2026-11-23 | Model name | FOUND | "Model: ollama/lfm3-omni:2b (LFM3 Omni 2B, 32k context)" (body) | no (4) |
| https://github.com/anomalyco/opencode/issues/61198 | agent: skill tool loops on invalid id instead of falling back | CLOSED | 2026-11-02 | 2026-11-23 | Session export is attached | FOUND (4) | "Session export attached by user (session-02cfc45e-de13-4e23-a741-81dedf339c3c.md)." (body) | no (4) |
| https://github.com/OpenHands/OpenHands/issues/8805 | [Bug]: Function 'execute_code' not found in available tools | CLOSED | 2025-05-30 | 2026-11-23 | Error message lists the available tools | FOUND | "Function 'execute_code' not found in available tools: ['execute_bash', 'think', 'finish', 'browser', 'execute_ipython_cell', 'str_replace_editor', 'fetch']" (body) | yes (5) |
| https://github.com/OpenHands/OpenHands/issues/8805 | [Bug]: Function 'execute_code' not found in available tools | CLOSED | 2025-05-30 | 2026-11-23 | OpenHands version 0.39 | FOUND | "0.39" (body; listed under the form heading "OpenHands Version") | yes (5) |
| https://github.com/OpenHands/OpenHands/issues/8805 | [Bug]: Function 'execute_code' not found in available tools | CLOSED | 2025-05-30 | 2026-11-23 | Model Devstral | FOUND | "I am getting the following error when using devstral as LLM." (body) | yes (5) |
| https://github.com/anthropics/claude-code/issues/63870 | [BUG] Bash tool calls emitted as raw &lt;invoke&gt; text instead of executing | OPEN | 2026-05-30 | 2026-11-23 | 23 malformed Bash blocks | FOUND | "Malformed raw invoke blocks: 23" (body) | yes (6) |
| https://github.com/anthropics/claude-code/issues/63870 | [BUG] Bash tool calls emitted as raw &lt;invoke&gt; text instead of executing | OPEN | 2026-05-30 | 2026-11-23 | 347 normal tool uses | FOUND | "Normal assistant structured tool uses: 347" (body) | yes (6) |
| https://github.com/anthropics/claude-code/issues/63870 | [BUG] Bash tool calls emitted as raw &lt;invoke&gt; text instead of executing | OPEN | 2026-05-30 | 2026-11-23 | Claude Code versions 2.1.156 and 2.1.158 | FOUND | "The affected transcript contains failures on both `2.1.156` and `2.1.158`." (body) | yes (6) |
| https://github.com/anthropics/claude-code/issues/104504 | [MODEL] "Tests pass" reported from a stale or piped run (measured across 150 sessions) | OPEN | 2026-10-23 | 2026-11-23 | 357 claims | FOUND | "We labelled 357 such claims from 150 Claude Code sessions" (body) | no |
| https://github.com/anthropics/claude-code/issues/104504 | [MODEL] "Tests pass" reported from a stale or piped run (measured across 150 sessions) | OPEN | 2026-10-23 | 2026-11-23 | 150 sessions | FOUND | "Across 150 of our real sessions, Claude was asked to make code changes" (body) | no |
| https://github.com/anthropics/claude-code/issues/104504 | [MODEL] "Tests pass" reported from a stale or piped run (measured across 150 sessions) | OPEN | 2026-10-23 | 2026-11-23 | "32" of "36" unbacked claims were stale | FOUND | "Of the 36 unbacked claims in our development set, 32 were stale" (body) | no |
| https://github.com/anthropics/claude-code/issues/104504 | [MODEL] "Tests pass" reported from a stale or piped run (measured across 150 sessions) | OPEN | 2026-10-23 | 2026-11-23 | Claude Code version | FOUND | "2.1.304 (Claude Code)" (body) | no |
| https://github.com/anthropics/claude-code/issues/105340 | [MODEL] Model fabricates &lt;task-notification&gt; and Monitor events in its own output, then reports results from them | OPEN | 2026-10-27 | 2026-11-23 | Claude Code version | FOUND | "2.1.304" (body; listed under the form heading "Claude Code Version") | no (7) |
| https://github.com/anthropics/claude-code/issues/105340 | [MODEL] Model fabricates &lt;task-notification&gt; and Monitor events in its own output, then reports results from them | OPEN | 2026-10-27 | 2026-11-23 | Model | FOUND | "Claude Opus 5.5 (`claude-opus-5-5`)." (body) | no (7) |
| https://github.com/anthropics/claude-code/issues/105340 | [MODEL] Model fabricates &lt;task-notification&gt; and Monitor events in its own output, then reports results from them | OPEN | 2026-10-27 | 2026-11-23 | Fabricated tool_use_id | FOUND | "It then emitted a `<task-notification>` for that task, with an invented tool_use_id ending `…vC7M`" (body) | no (7) |
| https://github.com/anthropics/claude-code/issues/105340 | [MODEL] Model fabricates &lt;task-notification&gt; and Monitor events in its own output, then reports results from them | OPEN | 2026-10-27 | 2026-11-23 | Fake Monitor events | FOUND | "Claude armed a Monitor on the still-running script, then wrote two fake Monitor events" (body) | no (7) |

## Notes

1. openai/codex#19765: no claims were listed for this issue. The body shows one example error line, introduced with the words "a log/error like". It does not quote a session log or JSONL file.
2. openai/codex#60081: the body contains a PowerShell command, introduced as "A sanitized excerpt of that launch". It contains no log or JSONL excerpt.
3. openai/codex#60081: the body opens with an AI disclosure saying GPT 6.1 Sol "prepared this report". The quoted line in the table is the body's own statement about the original generating model and Codex build.
4. anomalyco/opencode#61198: the body names the export file in text. The saved body contains no attachment link or file URL. The first bot comment thanks the reporter for the "session export". No session-log excerpt is in the body.
5. All-Hands-AI/OpenHands#8805: the body includes an agent log line (`08:05:40 - OBSERVATION`, then an `ErrorObservation`).
6. anthropics/claude-code#63870: the JSONL in the body is introduced as a "Representative malformed JSONL shape". Parts of it are cut short with `...`.
7. anthropics/claude-code#105340: the body describes records in the session JSONL but does not quote them. The comments describe further sessions and are not counted here.
