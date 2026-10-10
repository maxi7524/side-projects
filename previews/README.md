# Notebook previews

HTML previews show fresh outputs where execution completed, partial outputs where it stopped, or explicitly labeled historical/source-only content when required inputs or packages were unavailable.

**Viewing:** follow an HTML link, download the file from GitHub and open it in a browser. GitHub displays HTML source rather than a rendered notebook page.

Status totals: **blocked: 4**, **executed: 1**.

| Notebook | HTML | Status | Execution note |
|---|---|---|---|
| [Cat sleep analysis](../projects/cat-sleep-analysis/cat_analysis.ipynb) | [View/download](projects/cat-sleep-analysis/cat_analysis.html) | historical | Original saved plot; no new execution |
| [projects/frying-estimator/frying_estimator_notebook.ipynb](../projects/frying-estimator/frying_estimator_notebook.ipynb) | [View/download](projects/frying-estimator/frying_estimator_notebook.html) | executed | Fresh execution completed in source cell order with seed 4242. Historical results were not substituted. |
| [projects/virtual-cell-challenge/experiments/mithril-gears/gears_model.ipynb](../projects/virtual-cell-challenge/experiments/mithril-gears/gears_model.ipynb) | [View/download](projects/virtual-cell-challenge/experiments/mithril-gears/gears_model.html) | blocked | Unavailable original dependencies: gears, h5py, scanpy. Preserved historical outputs are shown for exactly matching cells; they are not results of a fresh run. |
| [projects/virtual-cell-challenge/experiments/single-cell-training/gears_model.ipynb](../projects/virtual-cell-challenge/experiments/single-cell-training/gears_model.ipynb) | [View/download](projects/virtual-cell-challenge/experiments/single-cell-training/gears_model.html) | blocked | Unavailable original dependencies: gears, h5py, scanpy. Preserved historical outputs are shown for exactly matching cells; they are not results of a fresh run. |
| [projects/virtual-cell-challenge/experiments/single-cell-training/gears_model_complexity.ipynb](../projects/virtual-cell-challenge/experiments/single-cell-training/gears_model_complexity.ipynb) | [View/download](projects/virtual-cell-challenge/experiments/single-cell-training/gears_model_complexity.html) | blocked | Unavailable original dependencies: gears, scanpy. Preserved historical outputs are shown for exactly matching cells; they are not results of a fresh run. |
| [projects/virtual-cell-challenge/experiments/single-cell-training/scRNA-seq.ipynb](../projects/virtual-cell-challenge/experiments/single-cell-training/scRNA-seq.ipynb) | [View/download](projects/virtual-cell-challenge/experiments/single-cell-training/scRNA-seq.html) | blocked | Unavailable original dependencies: scanpy, scvi. Preserved historical outputs are shown for exactly matching cells; they are not results of a fresh run. |

## Reproduction and interpretation

Runs used the existing Python 3.12 scientific environment without upgrading it. NumPy and Python random generators were seeded with 4242; source-defined seeds or random-generator instances may override this setup. A fresh run is execution evidence, not a scientific validation of a legacy algorithm.

Each cell was limited to 120 seconds and each notebook to 900 seconds. Later runs have a 4 GiB virtual-address-space limit. Missing packages, R kernels, installation cells and unavailable archived inputs remain explicit blockers. Failed/time-limited runs do not count as complete analyses. The week-11 stochastic exercise uses the owner-authorized reduced particle counts documented with its source.

Original source notebooks remain unchanged except the explicitly documented week-11 particle-count reduction. Generated inputs stay outside Git. HTML contains derived figures/tables for review. Machine-readable [execution status](execution-status.json) records source hashes and whether outputs are fresh or historical.

[Collection index](../README.md)
