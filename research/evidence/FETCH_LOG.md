# Fetch log

Fetched at 2026-11-23T12:51:50Z.

Method: the `gh` CLI was not installed on the capture machine, so `gh issue view` could not run. Every issue was fetched with the fallback: the unauthenticated GitHub REST API (`GET /repos/{owner}/{repo}/issues/{n}` and its `comments_url`), following redirects.

Each `<owner>_<repo>_<N>.json` file uses the same field names as `gh issue view --json number,title,state,createdAt,author,labels,url,body,comments`. Title, body and comment text are copied unchanged from the API. The untouched API responses are kept in `raw/`.

| Requested | Result | Final URL | Notes |
|---|---|---|---|
| openai/codex#29549 | OK via REST | https://github.com/openai/codex/issues/29549 | 1 comments. |
| openai/codex#19765 | OK via REST | https://github.com/openai/codex/issues/19765 | 0 comments. |
| openai/codex#60081 | OK via REST | https://github.com/openai/codex/issues/60081 | 1 comments. |
| anomalyco/opencode#21850 | OK via REST | https://github.com/anomalyco/opencode/issues/21850 | 4 comments. |
| anomalyco/opencode#61198 | OK via REST | https://github.com/anomalyco/opencode/issues/61198 | 2 comments. |
| All-Hands-AI/OpenHands#8805 | OK via REST (redirected to https://api.github.com/repositories/771302083/issues/8805) | https://github.com/OpenHands/OpenHands/issues/8805 | 7 comments. |
| anthropics/claude-code#63870 | OK via REST | https://github.com/anthropics/claude-code/issues/63870 | 25 comments. |
| anthropics/claude-code#104504 | OK via REST | https://github.com/anthropics/claude-code/issues/104504 | 4 comments. |
| anthropics/claude-code#105340 | OK via REST | https://github.com/anthropics/claude-code/issues/105340 | 2 comments. |

## Second batch

Fetched at 2026-11-23T16:22:11Z, the same way as above.

| Requested | Result | Final URL | Notes |
|---|---|---|---|
| anomalyco/opencode#33068 | OK via REST | https://github.com/anomalyco/opencode/issues/33068 | 1 comments. |
| anomalyco/opencode#15888 | OK via REST | https://github.com/anomalyco/opencode/issues/15888 | 1 comments. |
| anthropics/claude-code#79250 | OK via REST | https://github.com/anthropics/claude-code/issues/79250 | 2 comments. |
| anthropics/claude-code#87519 | OK via REST | https://github.com/anthropics/claude-code/issues/87519 | 2 comments. |
| anthropics/claude-code#93546 | OK via REST | https://github.com/anthropics/claude-code/issues/93546 | 1 comments. |
