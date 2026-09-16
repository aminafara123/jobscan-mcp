#!/usr/bin/env python3
"""jobscan-mcp: an MCP server over my job-scan-automation dataset.

Exposes the scanner's daily reports and dedupe memory as tools any
MCP-capable model can call (Claude Code, Claude Desktop, and friends).

Run (stdio):  python server.py
Wire into Claude Code:
  claude mcp add jobscan -- /path/to/.venv/bin/python /path/to/server.py
"""

import json
import re
from datetime import date, timedelta
from pathlib import Path

from mcp.server.mcpserver import MCPServer

DATA_DIR = Path.home() / "aiProjects/aminWork/job-research/scraper"

# Personal notes stripped before anything leaves this server.
STRIP_PREFIXES = ("Floor reminder", "Reminder:")

server = MCPServer(
    "jobscan",
    instructions=(
        "Tools over a daily job-market scan of remote and UAE-workable "
        "IT/GRC/cloud/AI postings. Reports are keyword-filtered, "
        "location-triaged, and deduplicated by the upstream scanner."
    ),
)


def _report_files():
    return sorted(DATA_DIR.glob("jobs-report-*.md"))


def _clean(text: str) -> str:
    lines = [l for l in text.splitlines()
             if not any(l.strip().startswith(p) for p in STRIP_PREFIXES)]
    return "\n".join(lines).strip()


@server.tool()
def latest_report() -> str:
    """Full text of the most recent daily scan report (markdown)."""
    files = _report_files()
    if not files:
        return "No reports found."
    return _clean(files[-1].read_text(encoding="utf-8"))


@server.tool()
def search_jobs(query: str, days: int = 14) -> str:
    """Search postings in the last N days of reports. Case-insensitive
    substring match over title/company lines; returns each hit with its
    link and the report date it appeared."""
    q = query.lower()
    hits, seen = [], set()
    for f in reversed(_report_files()):
        day = f.stem.replace("jobs-report-", "")
        try:
            if date.fromisoformat(day) < date.today() - timedelta(days=days):
                break
        except ValueError:
            continue
        lines = _clean(f.read_text(encoding="utf-8")).splitlines()
        for i, line in enumerate(lines):
            if line.startswith("- **") and q in line.lower():
                link = lines[i + 1].strip() if i + 1 < len(lines) else ""
                key = line.strip()
                if key not in seen:
                    seen.add(key)
                    hits.append(f"[{day}] {line.strip()}\n  {link}")
    if not hits:
        return f"No postings matching {query!r} in the last {days} days."
    return f"{len(hits)} match(es) for {query!r}:\n\n" + "\n".join(hits[:40])


@server.tool()
def market_stats(days: int = 30) -> str:
    """Per-day counts of relevant and new postings over the last N days,
    parsed from the reports: a quick pulse of the niche market."""
    rows = []
    for f in _report_files()[-days:]:
        day = f.stem.replace("jobs-report-", "")
        m = re.search(r"Kept (\d+) on-lane.*?\*\*(\d+) new",
                      f.read_text(encoding="utf-8"), re.S)
        if m:
            rows.append(f"{day}: {m.group(1)} relevant, {m.group(2)} new")
    if not rows:
        return "No parseable reports."
    total_new = sum(int(r.rsplit(" ", 2)[1]) for r in rows)
    return ("\n".join(rows)
            + f"\n\nTotal new postings across {len(rows)} report(s): {total_new}")


@server.tool()
def is_seen(company: str, title: str) -> str:
    """Whether the scanner's dedupe memory already contains this
    company+title posting (i.e. it has been surfaced before)."""
    state = DATA_DIR / "seen-jobs.json"
    if not state.exists():
        return "No dedupe memory found."
    key = re.sub(r"\W+", "", (company + title).lower())
    seen = set(json.loads(state.read_text(encoding="utf-8")))
    return ("SEEN: this posting has been surfaced before."
            if key in seen else
            "NOT SEEN: this would be new to the scanner.")


if __name__ == "__main__":
    server.run()
