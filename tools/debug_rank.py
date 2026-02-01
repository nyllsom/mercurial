# tools/debug_rank.py
from __future__ import annotations

import os, sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import argparse
import json
from pathlib import Path

from mercurial.config import load_settings
from mercurial.sources.arxiv_client import build_search_query, fetch_recent
from mercurial.ranker.simple_ranker import RankerConfig, rank_papers


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", action="append", default=None)
    parser.add_argument("--top", type=int, default=20)
    parser.add_argument("--dump", type=str, default=None, help="Dump ranked results to a JSON file")
    args = parser.parse_args()

    s = load_settings(selected_profiles=args.profile)
    q = build_search_query(s.arxiv_categories, s.keywords)

    print("=== SETTINGS ===")
    print("profiles:", s.profiles if s.profiles else "(none)")
    print("lookback_hours:", s.lookback_hours)
    print("max_fetch:", s.max_fetch)
    print("categories:", len(s.arxiv_categories))
    print("keywords:", len(s.keywords))
    print()
    print("=== arXiv query ===")
    print(q)
    print()

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

    print(f"Fetched {len(papers)} papers. Ranked {len(ranked)}.")
    print(f"Top {args.top}:")
    print("-" * 80)

    out = []
    for i, rp in enumerate(ranked[: args.top], 1):
        p = rp.paper
        b = rp.score_breakdown
        print(f"[{i}] score={rp.score:.4f} kw={b['kw_score']:.1f} recency={b['recency']:.3f} hrs={b['hours_ago']:.1f} cat_bonus={b['cat_bonus']:.2f}")
        print(f"    {p.title}")
        print(f"    hits: {', '.join(rp.matched_keywords[:12])}")
        print(f"    {p.abs_url}")
        print()

        out.append(
            {
                "rank": i,
                "score": rp.score,
                "matched_keywords": rp.matched_keywords,
                "score_breakdown": rp.score_breakdown,
                "paper": {
                    "arxiv_id": p.arxiv_id,
                    "version": p.version,
                    "title": p.title,
                    "authors": p.authors,
                    "abstract": p.abstract,
                    "categories": p.categories,
                    "published_at": p.published_at.isoformat(),
                    "updated_at": p.updated_at.isoformat(),
                    "abs_url": p.abs_url,
                    "pdf_url": p.pdf_url,
                },
            }
        )

    if args.dump:
        path = Path(args.dump)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Dumped to {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
