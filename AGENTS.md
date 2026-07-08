# AGENTS.md

Single source of truth for all AI agents (Hermes Agent, Claude Code, Gemini CLI, OpenCode).

## Project

**Yakhchal DataCenter** — PhD research project by Gonzalo Cayunao Erices (DISA, UNAB).

## Full Tech Stack

| Tool | Usage |
|------|-------|
| **Quarto** | Document authoring and rendering (QMD to PDF/LaTeX/XeLaTeX) |
| **Python >=3.14** | Numerical models, simulations, SciML |
| **uv** | Project management and dependency resolution |
| **ruff** | Python linting and formatting (PEP 8) |
| **Zotero** | Reference management and BibTeX bibliography |
| **VSCode** | Primary editor |
| **Claude Code** | AI coding assistant (Claude) |
| **OpenCode** | AI coding assistant (OpenAI) |
| **Gemini CLI** | AI coding assistant (Google) |
| **Hermes Agent** | AI agent (provider-agnostic) |

## Commands

```bash
uv sync                  # Sync environment
uv run <script.py>       # Run a Python script
ruff check               # Lint all Python files
ruff format              # Format all Python files
quarto render <file>.qmd --to pdf  # Render Quarto doc to PDF
```

## Python Dependencies

- quarto, amplpy, gurobipy, ipykernel, matplotlib, numpy, openpyxl, geopandas, pandas, pip, pulp, ruff, scikit-learn, scipy, seaborn

## Conventions

- Use **uv** exclusively — never pip directly
- Follow PEP 8 — use `ruff` for linting and formatting
- Research documents (.qmd) written in Spanish (lang: es)
- PDF engine: the IEEE paper (`docs/ieee-paper/`) renders via **Typst** (`format: ieee-typst`, quarto-ext/ieee extension); other .qmd documents use XeLaTeX with Latin Modern fonts
- PDFs are gitignored — always re-render from source .qmd files
- Zotero handles bibliography — export to .bib as needed
