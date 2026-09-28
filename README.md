# jobscan-mcp

[![M8ven Score](https://m8ven.ai/badge/mcp/aminafara123-jobscan-mcp-1c9wqy?v=98cb6d9d6c8106d3d0ccca8da34b74ff)](https://m8ven.ai/mcp/aminafara123-jobscan-mcp-1c9wqy)

An MCP server over my [job-scan-automation](https://github.com/aminafara123/job-scan-automation) dataset: the daily market scan behind [uae-remote-jobs-daily](https://github.com/aminafara123/uae-remote-jobs-daily), exposed as tools that any MCP-capable AI client can call.

MCP (Model Context Protocol) is the open standard for giving AI models controlled access to tools and data. This server is the pattern in miniature and in production: my own dataset, four read-only tools, and a model on the other end that can suddenly answer questions like "any new GRC postings this week?" with real data instead of guesses.

## Tools

| Tool | What it does |
|---|---|
| `latest_report()` | Full text of the most recent daily scan |
| `search_jobs(query, days)` | Search postings across the last N days of reports, links included |
| `market_stats(days)` | Per-day relevant/new counts: the pulse of the niche market |
| `is_seen(company, title)` | Whether the scanner's dedupe memory already knows a posting |

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install mcp
```

Wire it into Claude Code:

```bash
claude mcp add jobscan -- /path/to/jobscan-mcp/.venv/bin/python /path/to/jobscan-mcp/server.py
```

Then just ask: "check the job scan: anything new in IAM in the last week?" and watch the model call `search_jobs("IAM", 7)` on its own.

## Design notes

- **Read-only by construction.** Every tool reads files, nothing mutates the dataset. Giving a model tools means deciding what it must never be able to do, and here that decision is structural, not a prompt instruction.
- **Sanitization at the boundary.** The underlying reports can carry the operator's personal notes, so the server strips them before anything crosses the protocol. Data boundaries belong in code, not in hope.
- **Small on purpose.** Four tools, one file, standard library plus the `mcp` SDK. An MCP server doesnt need to be a platform to be useful. It just needs to expose the right verbs over data you actually maintain.

## About

Al Amin Bashir Afara, Dubai · [github.com/aminafara123](https://github.com/aminafara123) · [linkedin.com/in/aminafara](https://www.linkedin.com/in/aminafara)
