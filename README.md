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

Fetch then rank and print top N:

```bash
python -m mercurial.cli rank-only --profile llm --top 20
```

## 🔍 Debug Tools

Fetch debug (prints query and fetched papers):

```bash
python tools/fetch_arxiv.py
```

Rank debug (prints full breakdown + optionally dumps JSON):

```bash
python tools/debug_rank.py --profile llm --top 30 --dump data/debug/llm_rank.json
```

The JSON dump is designed to be a stable intermediate artifact for future stages (DB + frontend + delivery).

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
│   ├── fetch_arxiv.py
│   └── debug_rank.py
├── README.md
├── requirements.txt
└── requirements-dev.txt
```

## 🔮 Development Roadmap

Mercurial is built in **8 stages**, keeping boundaries clean and enabling layered verification.

1. ✅ **Stage 1 — arXiv Fetching** *(Completed: 2026-02-01)*

   * Fetch pipeline + `fetch-only`
   * Debug tool for query inspection

2. ✅ **Stage 2 — Ranker System** *(Completed: 2026-02-01)*

   * `RankedPaper` structure + explainable scoring breakdown
   * `rank-only` + JSON debug dump

3. **Stage 3 — LLM Digest Generation (Current)**

   * Turn Top ranked papers into a “liquid mercury” style Markdown digest
   * New modules (planned): `mercurial/digest/prompts.py`, `mercurial/digest/generator.py`
   * New CLI (planned): `digest-only` (fetch → rank → digest)

4. **Stage 4 — Database Integration (Idempotent + History)**

   * SQLite persistence for papers + digests (+ optional rankings)
   * Guarantee idempotency for daily runs (unless `--force`)
   * New module (planned): `mercurial/db.py`

5. **Stage 5 — Delivery: RSS + Email**

   * **5A: Dual RSS Feeds (MVP delivery)**

     * `papers.xml`: item = one `RankedPaper` (Top Papers feed)
     * `digests.xml`: item = one daily digest (Daily Digest feed)
   * **5B: Email Delivery**

     * Send HTML digest via SMTP/config flags
   * New modules (planned): `mercurial/delivery/rss.py`, `mercurial/delivery/emailer.py`

6. **Stage 6 — Single-File Web Frontend**

   * Local static UI to browse today’s digest + paper list
   * Read from `data/digests/*.md` and/or generated RSS

7. **Stage 7 — Service Mode (Backend/API + Public Feeds)**

   * HTTP API endpoints (planned): `/api/papers`, `/api/digest`
   * Feed endpoints (planned): `/rss/papers.xml`, `/rss/digests.xml`

8. **Stage 8 — Cloud Deployment & Automation**

   * Scheduled `run-daily` on server/function
   * Multi-profile feeds (e.g. `papers-llm.xml`, `digests-systems.xml`)
   * Production reliability: retries, logging, observability, backups

## 📄 License

MIT License
