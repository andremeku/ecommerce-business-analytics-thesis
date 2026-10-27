# Reproducibility and fidelity notes

- The original Colab notebook is preserved at `archive/original_thesis_notebook.ipynb`. It expects a dataset at `/content/Sales Transaction v.4a.csv`, so it needs its path adjusted when run locally.
- The `src/run_analysis.py` script is a new, portable portfolio refactor. It computes KPI measures, monthly revenue, top products, geographic revenue, Pareto revenue share, and **revenue-quantile customer tiers**. It deliberately does not claim to replicate every numeric figure in the thesis.
- The thesis describes **Recency–Frequency–Monetary (RFM) segmentation and clustering**, including four segments; the supplied notebook instead creates **Low/Medium/High tiers from customer revenue quartiles**. These two approaches should not be conflated.
- `src/rfm_clustering_extension.py` separately implements actual RFM features, log transformation, standardization and four-cluster K-means as a **new post-thesis portfolio extension**. Its cluster results are not presented as the exact thesis table values.
- The reported time period is inconsistent in parts of the thesis (November vs December 2018 start); for authoritative coverage refer to the actual parsed source CSV. The supplied CSV has 536,350 rows.
- The full source CSV is not hosted here. Obtain it from Kaggle and review the dataset license before any republication.
- Tableau `.twb` files do not include data and need connection relinking. The generated CSV exports provide five of the required Tableau source names; the combined dashboard's customer-level CSV contains newly assigned sequential surrogate IDs, not source customer identifiers.
- The original thesis PDF is included as an authored academic document. Confirm university/publication requirements before public distribution.

- The dataset ends on **9 December 2019**. Thus December 2019 represents a **partial month**, and its total should not be compared with full months as a seasonality effect.
