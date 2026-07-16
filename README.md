# Yakhchal DataCenter

**PhD Research Project** — *Application of Yakhchal (Ancient Persian Ice House) Technology as Water-Free Cooling Systems for Data Centers*

Gonzalo Cayunao Erices — DISA, Universidad Andrés Bello (UNAB)

## Overview

This project explores the feasibility of adapting the ancient Persian **Yakhchal** structure — a passive evaporative cooling system dating back to 400 BCE — as a modern, sustainable, **water-free cooling solution** for data centers. The goal is to reduce the environmental impact of data center thermal management, particularly in arid and semi-arid regions.

## Stack

| Tool | Purpose |
|------|---------|
| **Python ≥3.14** | Numerical models, simulations, SciML |
| **Quarto** | Research document authoring (QMD → PDF) |
| **uv** | Dependency management |
| **ruff** | Linting and formatting (PEP 8) |
| **Zotero** | Reference management (BibTeX) |

## Quick Start

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Run data pipelines:**
   ```bash
   uv run methods/solar_stations_pipeline.py
   uv run methods/wind_stations_pipeline.py
   uv run methods/curtailment_pipeline.py
   ```

3. **Precompute Stage 0 coefficients:**
   ```bash
   uv run methods/etapa0_precompute.py
   ```

4. **Calculate Curtailment Availability Index (CAI):**
   ```bash
   uv run methods/cai_pipeline.py
   ```

5. **Solve MILP (Base Scenario):**
   ```bash
   uv run methods/milp_model.py
   ```

6. **Run Sensitivity Grid (Pareto Front & CAPEX):**
   ```bash
   uv run methods/experimentos.py
   ```

7. **Generate Paper Figures:**
   ```bash
   uv run methods/figuras.py
   ```
   > [!NOTE]
   > All generated figure files (PDF/PNG) are gitignored. You must run this command to generate or update figures locally before compiling the document.

8. **Render Quarto Paper to PDF:**
   ```bash
   cd docs/ieee-paper && quarto render ieee-paper.qmd
   ```
   > [!NOTE]
   > The paper is rendered using the **Typst** engine (`format: ieee-typst`). The PDF file itself is gitignored and should be re-rendered from the source `.qmd` files as needed.


9. **Lint & Format code:**
   ```bash
   uv run ruff check .
   uv run ruff format .
   ```

## Repository Structure

```
├── docs/             # Research documents and feasibility studies
├── pitch-idea/       # Pitch and concept materials
└── sources/          # Cited papers and reference PDFs (gitignored)
```

## AI Usage Disclosure

The use of generative AI tools in this project is documented in [AI_USAGE.md](AI_USAGE.md).

## License

MIT — see [LICENSE](LICENSE)
