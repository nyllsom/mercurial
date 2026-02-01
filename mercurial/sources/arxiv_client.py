# mercurial/sources/arxiv_client.py
from __future__ import annotations

import re
from datetime import datetime, timezone, timedelta
from typing import List

import feedparser
import requests

from ..types import Paper


ARXIV_API = "https://export.arxiv.org/api/query"


def _parse_arxiv_id_and_version(entry_id: str) -> tuple[str, int]:
    # entry_id typically like: "http://arxiv.org/abs/1706.03762"
    m = re.search(r"/abs/([^v/]+)(?:v(\d+))?$", entry_id)
    if not m:
        # fallback: try last segment
        tail = entry_id.rstrip("/").split("/")[-1]
        m2 = re.match(r"([^v]+)v(\d+)", tail)
        if m2:
            return m2.group(1), int(m2.group(2))
        return tail, 1
    arxiv_id = m.group(1)
    ver = int(m.group(2) or "1")
    return arxiv_id, ver


def _dt(s: str) -> datetime:
    # e.g. "2026-01-31T01:23:45Z"
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    return datetime.fromisoformat(s).astimezone(timezone.utc).replace(tzinfo=None)


def build_search_query(categories: List[str], keywords: List[str]) -> str:
    # (cat:cs.AI OR cat:cs.LG) AND (all:"rag" OR all:"agent")
    cat_part = ""
    kw_part = ""

    if categories:
        cat_part = "(" + " OR ".join([f"cat:{c}" for c in categories]) + ")"
    if keywords:
        kw_part = "(" + " OR ".join([f'all:"{k}"' for k in keywords]) + ")"

    if cat_part and kw_part:
        return f"{cat_part} AND {kw_part}"
    if cat_part:
        return cat_part
    if kw_part:
        return kw_part
    return "all:*"


def fetch_recent(
    categories: List[str],
    keywords: List[str],
    lookback_hours: int,
    max_fetch: int,
) -> List[Paper]:
    """Fetch 'recently updated' papers, then locally filter by updated_at within lookback_hours."""
    q = build_search_query(categories, keywords)

    params = {
        "search_query": q,
        "start": 0,
        "max_results": max_fetch,
        "sortBy": "lastUpdatedDate",
        "sortOrder": "descending",
    }

    r = requests.get(ARXIV_API, params=params, timeout=30)
    r.raise_for_status()

    feed = feedparser.parse(r.text)
    now = datetime.utcnow()
    cutoff = now - timedelta(hours=lookback_hours)

    papers: List[Paper] = []

    for e in feed.entries:
        entry_id = getattr(e, "id", "")
        arxiv_id, version = _parse_arxiv_id_and_version(entry_id)

        title = re.sub(r"\s+", " ", (getattr(e, "title", "") or "")).strip()
        abstract = re.sub(r"\s+", " ", (getattr(e, "summary", "") or "")).strip()

        authors = [a.name for a in getattr(e, "authors", []) if getattr(a, "name", None)]
        categories_list = [t.term for t in getattr(e, "tags", []) if getattr(t, "term", None)]

        published_at = _dt(getattr(e, "published", "1970-01-01T00:00:00Z"))
        updated_at = _dt(getattr(e, "updated", getattr(e, "published", "1970-01-01T00:00:00Z")))

        if updated_at < cutoff:
            continue

        abs_url = f"https://arxiv.org/abs/{arxiv_id}"
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

        papers.append(
            Paper(
                arxiv_id=arxiv_id,
                version=version,
                title=title,
                authors=authors,
                abstract=abstract,
                categories=categories_list,
                published_at=published_at,
                updated_at=updated_at,
                abs_url=abs_url,
                pdf_url=pdf_url,
            )
        )

    return papers
