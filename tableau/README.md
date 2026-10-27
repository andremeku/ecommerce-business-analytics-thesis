# Tableau workbooks (.twb)

Six original Tableau workbooks have been preserved in this folder, with local machine paths in connection metadata replaced by repository-relative references.

**Note:** A `.twb` file contains Tableau workbook definitions, **not an embedded data extract**. GitHub cannot run or preview it as an interactive dashboard. Because the workbooks were originally authored with local Windows paths, opening them in Tableau Desktop/Public may prompt for a data-source reconnection.

1. Open a `.twb` file in Tableau Desktop/Public.
2. If prompted, reconnect the source to the corresponding `data/tableau_exports/*.csv` file.
3. The exports included here reproduce the relevant source columns and are derived by `src/run_analysis.py`; formatting and filters may require minor refresh or adjustment.
4. The combined `thesis_dashboard.twb` references `monthly_sales.csv`, `product_sales.csv`, and `customer_summary.csv`. The included `customer_summary.csv` uses **new sequential surrogate IDs**, not original customer identifiers; the measures are preserved for visualization, but lookups to original customers are intentionally impossible.

Files:
- `kpi_overview.twb` → `kpi_table.csv`
- `monthly_sales_trend.twb` → `monthly_sales.csv`
- `top_ten_products.twb` → `product_revenue.csv`
- `revenue_pareto.twb` → `product_pareto.csv`
- `global_revenue_map.twb` → `country_sales.csv`
- `thesis_dashboard.twb` → `monthly_sales.csv`, `product_sales.csv`, and `customer_summary.csv` (surrogate IDs)
