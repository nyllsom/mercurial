# mercurial/cli.py
from __future__ import annotations

import argparse
from textwrap import shorten

from .config import load_settings
from .profiles import list_profiles
from .sources.arxiv_client import fetch_recent


def cmd_fetch_only(profiles: list[str] | None) -> int:
    s = load_settings(selected_profiles=profiles)
    papers = fetch_recent(
        categories=s.arxiv_categories,
        keywords=s.keywords,
        lookback_hours=s.lookback_hours,
        max_fetch=s.max_fetch,
    )

    prof_str = ", ".join(s.profiles) if s.profiles else "(none)"
    print(f"Profiles: {prof_str}")
    print(f"Fetched {len(papers)} papers (lookback_hours={s.lookback_hours}, max_fetch={s.max_fetch}).")
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


def cmd_list_profiles() -> int:
    names = list_profiles()
    if not names:
        print("No profiles found. Create files like: profiles/llm.env")
        return 0

    print("Available profiles:")
    for n in names:
        print("-", n)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="mercurial")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_fetch = sub.add_parser("fetch-only", help="Only fetch papers from arXiv and print them")
    p_fetch.add_argument(
        "--profile",
        action="append",
        default=None,
        help="Enable a profile under ./profiles (can repeat). Example: --profile llm --profile systems",
    )

    sub.add_parser("profiles", help="List available profiles under ./profiles")

    args = parser.parse_args()

    if args.cmd == "fetch-only":
        return cmd_fetch_only(args.profile)

    if args.cmd == "profiles":
        return cmd_list_profiles()

    raise RuntimeError("Unknown command")


if __name__ == "__main__":
    raise SystemExit(main())
