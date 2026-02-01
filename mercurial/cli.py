# mercurial/cli.py
from __future__ import annotations

import argparse
from textwrap import shorten

from .config import load_settings

from .profiles import list_profiles
from .sources.arxiv_client import fetch_recent

from .ranker.simple_ranker import RankerConfig, rank_papers


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

def cmd_rank_only(profiles: list[str] | None, top: int | None) -> int:
    s = load_settings(selected_profiles=profiles)

    papers = fetch_recent(
        categories=s.arxiv_categories,
        keywords=s.keywords,
        lookback_hours=s.lookback_hours,
        max_fetch=s.max_fetch,
    )

    cfg = RankerConfig(
        keywords=s.keywords,
        title_weight=getattr(s, "kw_title_weight", 3.0),
        abstract_weight=getattr(s, "kw_abstract_weight", 1.0),
        recency_half_life_hours=getattr(s, "recency_half_life_hours", 48.0),
        category_bonus=getattr(s, "category_bonus", 0.2),
    )

    ranked = rank_papers(papers, cfg)
    n = top if top is not None else getattr(s, "top_picks", 20)

    prof_str = ", ".join(s.profiles) if s.profiles else "(none)"
    print(f"Profiles: {prof_str}")
    print(f"Fetched {len(papers)} papers -> Ranked {len(ranked)} papers. Showing top {n}.")
    print("-" * 80)

    for i, rp in enumerate(ranked[:n], 1):
        p = rp.paper
        hits = ", ".join(rp.matched_keywords[:8]) + ("..." if len(rp.matched_keywords) > 8 else "")
        b = rp.score_breakdown
        print(f"[{i}] score={rp.score:.4f}  kw={b['kw_score']:.1f}  recency={b['recency']:.3f}  hrs={b['hours_ago']:.1f}")
        print(f"    {p.arxiv_id}v{p.version} | {p.updated_at} UTC")
        print(f"    {p.title}")
        print(f"    hits: {hits}")
        print(f"    {p.abs_url}")
        print()

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

    p_rank = sub.add_parser("rank-only", help="Fetch then rank papers and print top picks")
    p_rank.add_argument("--profile", action="append", default=None, help="Enable a profile (repeatable)")
    p_rank.add_argument("--top", type=int, default=None, help="Show top N ranked papers")


    args = parser.parse_args()

    if args.cmd == "fetch-only":
        return cmd_fetch_only(args.profile)

    if args.cmd == "profiles":
        return cmd_list_profiles()
    
    if args.cmd == "rank-only":
        return cmd_rank_only(args.profile, args.top)

    raise RuntimeError("Unknown command")


if __name__ == "__main__":
    raise SystemExit(main())
