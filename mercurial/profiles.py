# mercurial/profiles.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import dotenv_values


def _split_csv(s: str) -> List[str]:
    return [x.strip() for x in s.split(",") if x.strip()]


@dataclass(frozen=True)
class Profile:
    name: str
    arxiv_categories: List[str]
    keywords: List[str]
    lookback_hours: Optional[int] = None
    max_fetch: Optional[int] = None


def profiles_dir() -> Path:
    # project_root/profiles
    return Path(__file__).resolve().parents[1] / "profiles"


def list_profiles() -> List[str]:
    d = profiles_dir()
    if not d.exists():
        return []
    names = []
    for p in d.glob("*.env"):
        names.append(p.stem)
    return sorted(names)


def load_profile(name: str) -> Profile:
    path = profiles_dir() / f"{name}.env"
    if not path.exists():
        raise FileNotFoundError(f"Profile not found: {name} ({path})")

    data: Dict[str, str] = {k: v for k, v in dotenv_values(path).items() if v is not None}

    cats = _split_csv(data.get("ARXIV_CATEGORIES", ""))
    kws = _split_csv(data.get("KEYWORDS", ""))

    lookback = data.get("LOOKBACK_HOURS")
    max_fetch = data.get("MAX_FETCH")

    return Profile(
        name=name,
        arxiv_categories=cats,
        keywords=kws,
        lookback_hours=int(lookback) if lookback else None,
        max_fetch=int(max_fetch) if max_fetch else None,
    )
