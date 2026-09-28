"""Smoke test over a synthetic dataset. Run: python test_server.py (or pytest)."""

import json
import tempfile
from datetime import date
from pathlib import Path

import server


def test_tools():
    with tempfile.TemporaryDirectory() as d:
        server.DATA_DIR = Path(d)
        day = date.today().isoformat()
        (server.DATA_DIR / f"jobs-report-{day}.md").write_text(
            "Kept 2 on-lane postings, **1 new**\n"
            "- **GRC Analyst** at Acme\n"
            "  https://example.com/grc\n"
            "Floor reminder: stretch\n"
            "- **Cloud Auditor** at Beta\n"
            "  https://example.com/cloud\n",
            encoding="utf-8",
        )
        (server.DATA_DIR / "seen-jobs.json").write_text(
            json.dumps(["acmegrcanalyst"]), encoding="utf-8"
        )

        report = server.latest_report()
        assert "GRC Analyst" in report
        assert "Floor reminder" not in report

        hits = server.search_jobs("grc")
        assert "1 match" in hits and "https://example.com/grc" in hits
        assert server.search_jobs("cobol").startswith("No postings")

        stats = server.market_stats()
        assert "2 relevant, 1 new" in stats
        assert "Total new postings across 1 report(s): 1" in stats

        assert server.is_seen("Acme", "GRC Analyst").startswith("SEEN")
        assert server.is_seen("Beta", "Cloud Auditor").startswith("NOT SEEN")


if __name__ == "__main__":
    test_tools()
    print("ok")
