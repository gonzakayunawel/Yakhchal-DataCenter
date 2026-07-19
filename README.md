# Multi-Objective Optimization for Datacenter Siting and Technology Selection in the Atacama Desert

**Yakhchal DataCenter Project** — PhD Research Project
*Gonzalo Cayunao Erices — Doctorado en Ingeniería de Sistemas Avanzados (DISA), Universidad Andrés Bello (UNAB)*

---

## Project Overview

This repository contains the implementation and source code of the research paper focused on solving the **optimal siting and technology selection problem for datacenters in the Atacama Desert, Chile**. The study addresses the critical trade-off between local water sustainability in extremely arid zones and the efficient grid integration of non-conventional renewable energy (NCRE) surpluses (curtailment).

The proposed framework operates in two hierarchical stages:

1. **Stage 0 (Climatic and Physical Precomputation):** Processes meteorological time-series from 10 candidate stations. Psychrometric variables like wet-bulb temperature ($T_{wb}$) are estimated using Stull's formula, and precipitable water ($PW$) is calculated. Using these thermodynamic variables, monthly Power Usage Effectiveness (**PUE**) and Water Usage Effectiveness (**WUE**) coefficients are precomputed for four cooling technologies:
   * **`H_CONV`**: Conventional water chiller coupled with a wet cooling tower.
   * **`H_ECO`**: Indirect evaporative air economizer (Indirect Evaporative Cooling - IEC).
   * **`H_RAD`**: Passive radiative cooling to outer space (extrapolating Aili et al.'s physical model coupled with a backup conventional chiller).
   * **`H_HYB`**: Hybrid cascading system prioritizing radiative cooling, followed by indirect evaporative cooling, using the conventional chiller only as a third-level backup.
2. **CAI (Curtailment Availability Index) Calculation:** A spatial sustainability indicator that quantifies the geodesic proximity of candidate sites to solar and wind generation plants experiencing energy curtailment, using exponential decay kernels parameterized by interconnection distance scales ($d_0$).
3. **Stage 1 (MILP Optimization Model):** A Mixed-Integer Linear Programming model scalarized via weighted sum to minimize annualized costs (CAPEX and OPEX) and water consumption, while maximizing NCRE surplus utilization (CAI), subject to budget constraints, strict climatic screening, and single technology allocation.

---

## Key Results

* **Siting Robustness:** **Salar (SLAR)** and **Crucero (CRUC)** consistently dominate the optimal locations under the baseline multi-objective scenario ($\alpha=0.4, \beta=0.3, \gamma=0.3, P=2, d_0=50$ km).
* **Technology Robustness:** The indirect economizer (**`H_ECO`**) dominates the selection in at least **95% of the sensitivity scenarios**, owing to its low capital cost and high thermal dissipation efficiency under Atacama's arid climate.
* **Water Conservation:** For a 2-site 1 MW IT load portfolio, the optimal configuration saves approximately **23,700 m³/year** of water (approx. 75% reduction) compared to conventional wet cooling towers (`H_CONV`).

---

## Repository Structure

The project structure is organized as follows:

* [methods/](file:///home/gonz4/Code/Yakhchal-DataCenter/methods) — Processing pipelines and optimization models:
  * [solar_stations_pipeline.py](file:///home/gonz4/Code/Yakhchal-DataCenter/methods/solar_stations_pipeline.py): Quality control (QC) and monthly aggregation of solar variables.
  * [wind_stations_pipeline.py](file:///home/gonz4/Code/Yakhchal-DataCenter/methods/wind_stations_pipeline.py): Quality control and monthly aggregation of wind variables.
  * [curtailment_pipeline.py](file:///home/gonz4/Code/Yakhchal-DataCenter/methods/curtailment_pipeline.py): Consolidation and georeferencing of renewable generation curtailments from the National Electrical Coordinator (CEN).
  * [etapa0_precompute.py](file:///home/gonz4/Code/Yakhchal-DataCenter/methods/etapa0_precompute.py): Precomputation of psychrometric variables, climatic screening ($z_i$), and PUE/WUE matrices per technology and site.
  * [cai_pipeline.py](file:///home/gonz4/Code/Yakhchal-DataCenter/methods/cai_pipeline.py): Calculation of the CAI index per site for sensitivity scales of $d_0 \in \{20, 50, 100\}$ km.
  * [milp_model.py](file:///home/gonz4/Code/Yakhchal-DataCenter/methods/milp_model.py): Mixed-Integer Linear Programming model formulation using Gurobi.
  * [experimentos.py](file:///home/gonz4/Code/Yakhchal-DataCenter/methods/experimentos.py): Sensitivity grid sweep over objective weights ($\alpha, \beta, \gamma$), $d_0$ scales, site count $P$, and CAPEX variations ($\pm 50\%$).
  * [figuras.py](file:///home/gonz4/Code/Yakhchal-DataCenter/methods/figuras.py): Programmatic generation of paper figures and maps.
* [docs/](file:///home/gonz4/Code/Yakhchal-DataCenter/docs) — Academic documentation and feasibility reports:
  * [PLAN_PAPER.md](file:///home/gonz4/Code/Yakhchal-DataCenter/docs/PLAN_PAPER.md): Track of project milestones and methodological gap resolutions.
  * [ieee-paper/](file:///home/gonz4/Code/Yakhchal-DataCenter/docs/ieee-paper) — Manuscript source files:
    * [ieee-paper.qmd](file:///home/gonz4/Code/Yakhchal-DataCenter/docs/ieee-paper/ieee-paper.qmd): Quarto document in Spanish using the Typst engine (`format: ieee-typst`) to render the IEEE-formatted paper PDF.
    * `refs.bib`: BibTeX bibliography file managed via Zotero.
* [results/](file:///home/gonz4/Code/Yakhchal-DataCenter/results) — Numeric outputs and validation reports from experiments.
* [figures/](file:///home/gonz4/Code/Yakhchal-DataCenter/figures) — Reproducible graphics and study area maps (gitignored, generated locally).
* [data/](file:///home/gonz4/Code/Yakhchal-DataCenter/data) — Raw climatological data from Walker Network and CEN curtailment logs. Most source files and consolidated datasets (e.g. `curtailment_acumulado.csv`) are committed; large cached station CSVs and manual GIS exports are gitignored (see [Quick Start Guide](#quick-start-guide) step 2).

---

## Tech Stack & Dependencies

| Tool | Usage / Purpose |
| :--- | :--- |
| **Python $\ge$ 3.14** | Numerical modeling, physical balance simulations, and data wrangling. |
| **Quarto CLI** | Academic document compiler to render PDF papers via **ieee-typst**. System binary, installed separately (see note below). |
| **Typst** | Typesetting engine invoked by Quarto's `ieee-typst` format. System binary, installed separately (see note below). |
| **uv** | Fast, deterministic Python package installer and dependency resolver. |
| **Gurobi Optimizer** | Industrial-grade solver used to solve the Stage 1 MILP model. |
| **ruff** | Python linter and formatter enforcing PEP 8 style guide compliance. |
| **Zotero** | Reference manager for export and curation of `refs.bib`. |

### Primary Python Dependencies:
`gurobipy`, `pandas`, `numpy`, `matplotlib`, `seaborn`, `geopandas`, `scipy`, `scikit-learn`, `ruff`, `quarto`.

> [!NOTE]
> The `quarto` entry above is a thin Python wrapper — it does **not** install the Quarto CLI itself. Quarto and Typst are system binaries that `uv sync` cannot resolve; see step 8 of the Quick Start Guide for install instructions.

---

## Quick Start Guide

Follow these steps in order to sync your environment, process the datasets, solve the optimization model, and render the final paper:

1. **Install and synchronize dependencies:**
   ```bash
   uv sync
   ```

2. **Run data pipelines for quality control and preprocessing:**
   ```bash
   uv run methods/solar_stations_pipeline.py
   uv run methods/wind_stations_pipeline.py
   uv run methods/curtailment_pipeline.py
   ```
   > [!IMPORTANT]
   > `curtailment_pipeline.py` georeferences plants using ESRI shapefiles manually exported from the [IDE Energía web viewer](https://ide-energia.minenergia.cl/portal/apps/webappviewer/index.html?id=5c526a138b1449458e0667b2235d2b19) (not a stable download URL, so it can't be automated). These exports (`data/output*.zip`) are gitignored and **not required** to reproduce the paper: `data/curtailment_acumulado.csv` is already committed with the exact dataset used in the study, so on a fresh clone you can skip this script entirely. Only rerun it if you need to regenerate the dataset (e.g. with newer CEN reports) — in that case, export the `Solares` and `Eólica` layers from the viewer per map viewport, save each export as `data/output.zip`, `data/output (1).zip`, etc., then run the script.

3. **Precompute Stage 0 coefficients (PUE/WUE matrix):**
   ```bash
   uv run methods/etapa0_precompute.py
   ```

4. **Calculate geodesic Curtailment Availability Index (CAI):**
   ```bash
   uv run methods/cai_pipeline.py
   ```

5. **Solve the MILP model (Base Scenario):**
   ```bash
   uv run methods/milp_model.py
   ```

6. **Run sensitivity grid search (726 scenarios):**
   ```bash
   uv run methods/experimentos.py
   ```

7. **Generate publication-ready figures:**
   ```bash
   uv run methods/figuras.py
   ```
   > [!NOTE]
   > Figure files will be saved in `figures/`. This directory is gitignored to avoid versioning binary files.

8. **Render the Quarto paper to PDF:**
   ```bash
   cd docs/ieee-paper && quarto render ieee-paper.qmd
   ```
   > [!NOTE]
   > The paper is compiled using **Typst** for high rendering speeds and typesetting quality. The output PDF is gitignored.

   > [!IMPORTANT]
   > This step requires the **Quarto** and **Typst** CLI binaries on your `PATH`. Neither is installed by `uv sync` — the `quarto` PyPI package is only a Python wrapper that shells out to the real `quarto` binary. Install both as regular system binaries (no `sudo` needed — both ship as self-contained tarballs):
   > ```bash
   > # Quarto (get the current version/URL from https://quarto.org/docs/get-started/)
   > curl -L -o quarto.tar.gz https://github.com/quarto-dev/quarto-cli/releases/latest/download/quarto-1.9.38-linux-amd64.tar.gz
   > mkdir -p ~/.local/opt && tar -xzf quarto.tar.gz -C ~/.local/opt && mv ~/.local/opt/quarto-*/ ~/.local/opt/quarto
   > ln -sf ~/.local/opt/quarto/bin/quarto ~/.local/bin/quarto
   >
   > # Typst (get the current version/URL from https://github.com/typst/typst/releases)
   > curl -L -o typst.tar.xz https://github.com/typst/typst/releases/latest/download/typst-x86_64-unknown-linux-musl.tar.xz
   > tar -xJf typst.tar.xz && cp typst-*/typst ~/.local/bin/typst && chmod +x ~/.local/bin/typst
   > ```
   > Make sure `~/.local/bin` is on your `PATH`, then verify with `quarto --version` and `typst --version`.

9. **Lint & Format code (Style Check):**
   ```bash
   uv run ruff check .
   uv run ruff format .
   ```

---

## Quality Control & Guidelines

* **Methodological Rigor:** Georeferenced curtailment and monthly climatology datasets are verified by quality control filters against physical bounds (fully documented in [PLAN_PAPER.md](file:///home/gonz4/Code/Yakhchal-DataCenter/docs/PLAN_PAPER.md)).
* **AI Disclosure:** Usage of generative AI tools throughout this academic workflow is disclosed in [AI_USAGE.md](file:///home/gonz4/Code/Yakhchal-DataCenter/AI_USAGE.md).
* **License:** Distributed under the MIT License. See [LICENSE](file:///home/gonz4/Code/Yakhchal-DataCenter/LICENSE) for more information.
