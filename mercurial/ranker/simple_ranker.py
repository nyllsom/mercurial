# mercurial/ranker/simple_ranker.py
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List, Tuple

from ..types import Paper, RankedPaper


def _normalize(text: str) -> str:
    # lower + collapse spaces
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def _keyword_hits(text: str, keywords: Iterable[str]) -> List[str]:
    t = _normalize(text)
    hits = []
    for kw in keywords:
        k = _normalize(kw)
        if not k:
            continue
        # TODO： update to token/regex
        if k in t:
            hits.append(kw)
    return hits


def _hours_ago(now: datetime, past: datetime) -> float:
    delta = now - past
    return max(delta.total_seconds() / 3600.0, 0.0)


def _recency_score(hours_ago: float, half_life_hours: float) -> float:
    # exp decay: score = 2^(-t/half_life)
    if half_life_hours <= 0:
        return 1.0
    return 2 ** (-hours_ago / half_life_hours)


@dataclass(frozen=True)
class RankerConfig:
    keywords: List[str]
    title_weight: float = 3.0
    abstract_weight: float = 1.0
    recency_half_life_hours: float = 48.0
    category_bonus: float = 0.2
    bonus_categories: Tuple[str, ...] = (
        # TODO: modify according to personal interest
        "cs.AI", "cs.LG", "cs.CL", "cs.CV", "cs.RO",
        "cs.DC", "cs.OS", "cs.NI", "cs.PL", "cs.SE", "cs.LO", "cs.AR",
        "stat.ML", "math.OC", "eess.SY",
    )


def rank_papers(papers: List[Paper], cfg: RankerConfig, now: datetime | None = None) -> List[RankedPaper]:
    now = now or datetime.utcnow()

    ranked: List[RankedPaper] = []

    for p in papers:
        title_hits = _keyword_hits(p.title, cfg.keywords)
        abs_hits = _keyword_hits(p.abstract, cfg.keywords)

        uniq_hits = []
        seen = set()
        for k in title_hits + abs_hits:
            if k not in seen:
                uniq_hits.append(k)
                seen.add(k)

        kw_score = cfg.title_weight * len(title_hits) + cfg.abstract_weight * len(abs_hits)

        hrs = _hours_ago(now, p.updated_at)
        recency = _recency_score(hrs, cfg.recency_half_life_hours)

        cat_bonus = 0.0
        if any(c in cfg.bonus_categories for c in p.categories):
            cat_bonus = cfg.category_bonus

        score = kw_score * recency + cat_bonus

        breakdown = {
            "kw_score": float(kw_score),
            "recency": float(recency),
            "cat_bonus": float(cat_bonus),
            "hours_ago": float(hrs),
        }

        ranked.append(
            RankedPaper(
                paper=p,
                score=float(score),
                matched_keywords=uniq_hits,
                score_breakdown=breakdown,
            )
        )

    ranked.sort(key=lambda rp: (rp.score, rp.paper.updated_at), reverse=True)
    return ranked
