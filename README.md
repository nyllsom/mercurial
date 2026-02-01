# Mercurial

**arXiv Tracker that Flows Like Liquid Mercury**

An elegant, configurable arXiv paper subscription and retrieval tool. It fetches recent papers from arXiv, then **ranks** them with a lightweight scoring model (keywords + recency decay + optional category bonus). Built with a **profiles** system so you can track multiple research areas cleanly.

## ✨ Core Features

- **arXiv Integration**: Fetches recent papers from arXiv based on categories (+ optional keywords).
- **Configuration-Driven**: Preferences live in `.env` and/or `profiles/*.env`.
- **Multi-Profile System**: Switch or combine research areas via profiles (e.g., `llm.env`, `system.env`, `math.env`).
- **Built-in Ranker (Stage 2)**: Scores and sorts papers by:
  - keyword hits in title/abstract
  - exponential time decay (half-life hours)
  - optional category bonus
- **Clean CLI + Debug Tools**:
  - `fetch-only` / `rank-only`
  - standalone debug scripts that can dump JSON for future DB/frontend work
- **Conventional Commits Enforcement**: Commit messages are validated via a `commit-msg` hook (powered by `pre-commit`).

## 🚀 Quick Start

### Installation

```bash
git clone <your-repo-url>
cd mercurial
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
````

### Configuration

This project reads environment variables from `.env` (optional) and merges with selected profiles under `profiles/`.

Typical setup:

1. Create a `.env` at repo root (or just rely on profiles):

   ```bash
   # example
   PROFILES=llm,system
   LOOKBACK_HOURS=72
   MAX_FETCH=200
   ```

2. Use profiles in `profiles/*.env` to define categories/keywords/settings for different domains.

> Note: `data/` is ignored by git (`.gitignore` includes `data/`). Debug dumps and cache files should go there.

## 🧰 CLI Usage

List available profiles:

```bash
python -m mercurial.cli profiles
```

Fetch papers (uses selected profiles or default env):

```bash
python -m mercurial.cli fetch-only
```

Fetch using one or more profiles:

```bash
python -m mercurial.cli fetch-only --profile llm --profile system
```

Fetch without keywords (category-only fetch):

```bash
python -m mercurial.cli fetch-only --no-keywords
```

Fetch then rank and print top N:

```bash
python -m mercurial.cli rank-only --profile llm --top 20
```

## 🔍 Debug Tools

Fetch debug (prints query and fetched papers):

```bash
python tools/debug_fetch_arxiv.py --profile llm
```

Rank debug (prints full breakdown + optionally dumps JSON):

```bash
python tools/debug_rank.py --profile llm --top 30 --dump data/debug/llm_rank.json
```

The JSON dump is designed to be a stable intermediate artifact for future stages (DB + frontend).

## ✅ Commit Message Convention (Conventional Commits)

This repo enforces **Conventional Commits** via a `commit-msg` hook using `pre-commit`.
If a commit message does not match the format, the commit will be rejected.

### Setup (one-time)

Install dev dependencies:

```bash
pip install -r requirements-dev.txt
```

Install git hooks:

```bash
pre-commit install --hook-type commit-msg --hook-type pre-commit
```

### Format

```
<type>(<scope>): <subject>
```

Examples:

* `feat(ranker): implement simple keyword+recency ranker`
* `fix(sources): handle missing arxiv version`
* `docs(readme): update usage and roadmap`
* `chore(dev): enforce conventional commits with pre-commit`

Common scopes for this project:

* `cli`, `ranker`, `sources`, `config`, `profiles`, `types`, `tools`, `readme`, `stage1`, `stage2`

## ⚙️ Ranker Scoring Model (Stage 2)

Rank output is a list of `RankedPaper`:

* `paper`: original paper object
* `score`: final score
* `matched_keywords`: unique matched keywords
* `score_breakdown`: debug-friendly components (`kw_score`, `recency`, `hours_ago`, `cat_bonus`)

Ranker parameters (via env / profiles):

```env
# ranker
TOP_PICKS=20
KW_TITLE_WEIGHT=3.0
KW_ABSTRACT_WEIGHT=1.0
RECENCY_HALF_LIFE_HOURS=48
CATEGORY_BONUS=0.2
```

## 📁 Project Structure

```
.
├── mercurial/
│   ├── cli.py
│   ├── config.py
│   ├── profiles.py
│   ├── types.py
│   ├── sources/
│   │   └── arxiv_client.py
│   ├── ranker/
│   │   └── simple_ranker.py
│   └── tools/
├── profiles/
├── tools/
│   ├── debug_fetch_arxiv.py
│   └── debug_rank.py
├── README.md
├── requirements.txt
└── requirements-dev.txt
```

## 🔮 Development Roadmap

Planned stages:

1. ✅ **arXiv Fetching** - *Completed (2026.2.1)*
2. ✅ **Ranker** - *Completed (2026.2.1)*
3. **LLM Digest Generation** - Generate daily/weekly summaries for top picks.
4. **Database Integration** - Persistent storage for papers, ranks, and digests.
5. **Email Delivery** - Automated digest delivery.
6. **Single-File Web Frontend** - Simple local UI for browsing digests.
7. **Frontend-Backend Decoupling** - Formal API backend + separate frontend.
8. **Cloud Deployment** - Production deployment.

## 📄 License

MIT License

