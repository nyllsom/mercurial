# Mercurial

**arXiv Tracker that Flows Like Liquid Mercury**

An elegant, configurable arXiv paper subscription and retrieval tool that supports intelligent filtering based on categories and keywords, with a built-in profiles system for multi-disciplinary research tracking.

## ✨ Core Features

- **arXiv Integration**: Fetches latest papers from arXiv API based on specified categories and keywords.
- **Configuration-Driven**: Flexible subscription preferences through `.env` files.
- **Multi-Profile System**: Easily switch between research areas using pre-configured profiles (e.g., `llm.env`, `systems.env`).
- **Clean CLI**: Intuitive command-line interface for fetching and profile management.

## 🚀 Quick Start

### Installation & Configuration

1.  **Clone and install dependencies**
    ```bash
    git clone <your-repo-url>
    cd mercurial
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Basic configuration**
    ```bash
    cp .env.example .env
    # Edit .env to set your arXiv categories and keywords
    ```

3.  **Use pre-configured profiles (optional)**
    The project includes pre-configured profiles for different research areas (located in `profiles/`).
    Enable multiple profiles by setting `PROFILES=llm,systems` in `.env`.

### Basic Usage

List available profiles:
```bash
python -m mercurial.cli profiles
```

Fetch and print papers (using default .env configuration):
```bash
python -m mercurial.cli fetch-only
```

Fetch using one or more specific profiles:
```bash
python -m mercurial.cli fetch-only --profile llm --profile systems
```

Debug script (standalone):
```bash
python tools/fetch_arxiv.py
```

## 📁 Project Structure

```
.
├── .env.example              # Environment variable template
├── .gitignore               # Git ignore rules
├── README.md                # Project documentation
├── requirements.txt         # Python dependencies
├── profiles/                # Pre-configured profile files (llm.env, system.env, ...)
├── data/                    # Data directory (auto-created, not committed to Git)
├── mercurial/               # Main package directory
│   ├── __init__.py
│   ├── cli.py              # Command-line interface
│   ├── config.py           # Configuration loading and merging
│   ├── profiles.py         # Profile management system
│   ├── types.py            # Paper data class
│   ├── sources/            # Data source modules
│   │   ├── __init__.py
│   │   └── arxiv_client.py # arXiv API client
│   └── tools/              # Tool module package (reserved)
│       └── __init__.py
└── tools/                  # Standalone debug scripts
    └── fetch_arxiv.py      # arXiv fetching debug script
```

## 🔮 Development Roadmap

According to the development plan, this project will evolve through the following stages:

1.  ✅ **arXiv Fetching** - *Completed (2026.2.1)*
2.  ➡️ **Ranker** - Score and sort fetched papers based on relevance.
3.  **LLM Digest Generation** - Use large language models to generate daily summaries of selected papers.
4.  **Database Integration** - Persistent storage for papers and digest records.
5.  **Email Delivery** - Automatically send generated digests to email.
6.  **Single-File Web Frontend** - Simple local interface for viewing digests.
7.  **Frontend-Backend Decoupling** - Build formal API backend and frontend.
8.  **Cloud Deployment** - Implement full cloud service.

## 📄 License

MIT License