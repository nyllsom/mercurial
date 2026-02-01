# mercurial/types.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class Paper:
    arxiv_id: str
    version: int
    title: str
    authors: List[str]
    abstract: str
    categories: List[str]
    published_at: datetime   # naive UTC
    updated_at: datetime     # naive UTC
    abs_url: str
    pdf_url: str
