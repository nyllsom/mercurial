# mercurial/cli.py
from __future__ import annotations

import argparse
from textwrap import shorten

from .config import load_settings
from .sources.arxiv_client import fetch_recent


def cmd_fetch_only() -> int:
    s = load_settings()
    papers = fetch_recent(
        categories=s.arxiv_categories,
        keywords=s.keywords,
        lookback_hours=s.lookback_hours,
        max_fetch=s.max_fetch,
    )

    print(f"Fetched {len(papers)} papers (lookback_hours={s.lookback_hours}).")
    print("-" * 80)

    for i, p in enumerate(papers, 1):
        authors = ", ".join(p.authors[:5]) + ("..." if len(p.authors) > 5 else "")
        print(f"[{i}] {p.arxiv_id}v{p.version} | {p.updated_at} UTC")
        print(f"    {p.title}")
        print(f"    Authors: {authors}")
        print(f"    {shorten(p.abstract, width=200, placeholder='...')}")
        print(f"    {p.abs_url}")
        print()

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="mercurial")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("fetch-only", help="Only fetch papers from arXiv and print them")

    args = parser.parse_args()

    if args.cmd == "fetch-only":
        return cmd_fetch_only()

    raise RuntimeError("Unknown command")


if __name__ == "__main__":
    raise SystemExit(main())
