# tools/fetch_arxiv.py
from __future__ import annotations

from mercurial.config import load_settings
from mercurial.sources.arxiv_client import build_search_query, fetch_recent


def main() -> int:
    s = load_settings()
    q = build_search_query(s.arxiv_categories, s.keywords)

    print("=== SETTINGS ===")
    print("categories:", s.arxiv_categories)
    print("keywords:", s.keywords)
    print("lookback_hours:", s.lookback_hours)
    print("max_fetch:", s.max_fetch)
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

    print(f"=== RESULT: {len(papers)} papers ===")
    if papers:
        print("Top 3:")
        for p in papers[:3]:
            print("-", p.arxiv_id, "v", p.version, "|", p.title)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
