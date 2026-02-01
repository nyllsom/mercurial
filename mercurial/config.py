# mercurial/config.py
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv


def _split_csv(s: str) -> List[str]:
    return [x.strip() for x in s.split(",") if x.strip()]


@dataclass(frozen=True)
class Settings:
    arxiv_categories: List[str]
    keywords: List[str]
    lookback_hours: int
    max_fetch: int


def load_settings() -> Settings:
    load_dotenv()

    categories = _split_csv(os.getenv("ARXIV_CATEGORIES", ""))
    keywords = _split_csv(os.getenv("KEYWORDS", ""))

    lookback_hours = int(os.getenv("LOOKBACK_HOURS", "24"))
    max_fetch = int(os.getenv("MAX_FETCH", "50"))

    return Settings(
        arxiv_categories=categories,
        keywords=keywords,
        lookback_hours=lookback_hours,
        max_fetch=max_fetch,
    )
