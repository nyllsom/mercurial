# mercurial/config.py
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Optional, Sequence

from dotenv import load_dotenv

from .profiles import list_profiles, load_profile


def _split_csv(s: str) -> List[str]:
    return [x.strip() for x in s.split(",") if x.strip()]


def _unique(seq: Sequence[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for x in seq:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out


@dataclass(frozen=True)
class Settings:
    arxiv_categories: List[str]
    keywords: List[str]
    lookback_hours: int
    max_fetch: int
    profiles: List[str]
    top_picks: int
    kw_title_weight: float
    kw_abstract_weight: float
    recency_half_life_hours: float
    category_bonus: float


def load_settings(selected_profiles: Optional[List[str]] = None) -> Settings:
    """
    Priority:
      1) selected_profiles passed from CLI
      2) PROFILES in .env
      3) legacy ARXIV_CATEGORIES/KEYWORDS in .env (also treated as base additions)
    Merge strategy:
      - categories/keywords: UNION(base + all profiles)
      - lookback_hours/max_fetch: .env default, can be overridden by profile if profile defines it
        (if multiple profiles define it, we take the max to be safe)
    """
    load_dotenv()

    base_categories = _split_csv(os.getenv("ARXIV_CATEGORIES", ""))
    base_keywords = _split_csv(os.getenv("KEYWORDS", ""))

    # global defaults
    lookback_hours = int(os.getenv("LOOKBACK_HOURS", "72"))
    max_fetch = int(os.getenv("MAX_FETCH", "200"))

    env_profiles = _split_csv(os.getenv("PROFILES", ""))
    profiles = selected_profiles if selected_profiles is not None else env_profiles

    top_picks = int(os.getenv("TOP_PICKS", "20"))
    kw_title_weight = float(os.getenv("KW_TITLE_WEIGHT", "3.0"))
    kw_abstract_weight = float(os.getenv("KW_ABSTRACT_WEIGHT", "1.0"))
    recency_half_life_hours = float(os.getenv("RECENCY_HALF_LIFE_HOURS", "48"))
    category_bonus = float(os.getenv("CATEGORY_BONUS", "0.2"))

    # Merge profiles
    all_categories: List[str] = list(base_categories)
    all_keywords: List[str] = list(base_keywords)

    prof_lookbacks: List[int] = []
    prof_maxfetch: List[int] = []

    if profiles:
        available = set(list_profiles())
        for name in profiles:
            if name not in available:
                raise ValueError(f"Unknown profile: {name}. Available: {sorted(available)}")

            p = load_profile(name)
            all_categories.extend(p.arxiv_categories)
            all_keywords.extend(p.keywords)

            if p.lookback_hours is not None:
                prof_lookbacks.append(p.lookback_hours)
            if p.max_fetch is not None:
                prof_maxfetch.append(p.max_fetch)

    # take the max if profiles specify overrides (safer for coverage)
    if prof_lookbacks:
        lookback_hours = max([lookback_hours, *prof_lookbacks])
    if prof_maxfetch:
        max_fetch = max([max_fetch, *prof_maxfetch])

    return Settings(
        arxiv_categories=_unique(all_categories),
        keywords=_unique(all_keywords),
        lookback_hours=lookback_hours,
        max_fetch=max_fetch,
        profiles=profiles,
        top_picks=top_picks,
        kw_title_weight=kw_title_weight,
        kw_abstract_weight=kw_abstract_weight,
        recency_half_life_hours=recency_half_life_hours,
        category_bonus=category_bonus,
    )
