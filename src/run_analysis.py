"""Reproducible descriptive e-commerce analysis and Tableau-compatible exports.

Portfolio refactor of the source thesis notebook, not a verbatim reproduction.
See README for differences and limitations.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REQUIRED = {
    "TransactionNo", "Date", "ProductNo", "ProductName",
    "Price", "Quantity", "CustomerNo", "Country"
}


def load_transactions(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"TransactionNo": "string", "ProductNo": "string", "CustomerNo": "string"})
    missing = REQUIRED.difference(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce", format="%m/%d/%Y")
    if df["Date"].isna().all():
        raise ValueError("No valid dates found; expected MM/DD/YYYY format")
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df["TotalValue"] = df["Price"] * df["Quantity"]
    return df


def save_plot(path: Path) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=170, bbox_inches="tight")
    plt.close()


def run(input_path: Path, export_dir: Path, figure_dir: Path) -> dict:
    export_dir.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)
    df = load_transactions(input_path)
    cancelled = df["TransactionNo"].fillna("").str.startswith("C") | (df["Quantity"] <= 0)
    clean = df.loc[(~cancelled) & df["Date"].notna() & (df["Price"] > 0)].copy()
    # Customer IDs without values are retained for transaction-level analysis
    # but excluded from customer-level segmentation.
    clean["YearMonth"] = clean["Date"].dt.strftime("%Y-%m")
    total_revenue = float(clean["TotalValue"].sum())
    transaction_count = int(clean["TransactionNo"].nunique())
    known_customers = int(clean["CustomerNo"].nunique())
    cancel_rate = float(cancelled.mean())
    kpi = pd.DataFrame({"Metric": ["Total revenue", "Transactions", "Known customers", "Average transaction value", "Cancelled line rate"],
                        "Value": [total_revenue, transaction_count, known_customers,
                                  total_revenue / max(transaction_count, 1), cancel_rate]})
    kpi.to_csv(export_dir / "kpi_table.csv", index=False)

    monthly = (clean.groupby("YearMonth", as_index=False)["TotalValue"].sum())
    monthly["Date"] = pd.to_datetime(monthly["YearMonth"] + "-01")
    monthly[["Date", "YearMonth", "TotalValue"]].to_csv(export_dir / "monthly_sales.csv", index=False, date_format="%Y-%m-%d")
    fig, ax = plt.subplots(figsize=(10, 4.4))
    ax.plot(monthly["YearMonth"], monthly["TotalValue"] / 1e6, marker="o", linewidth=2)
    ax.set_title("Monthly Revenue Trend")
    ax.set_ylabel("Revenue (£ millions)")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", alpha=0.25)
    save_plot(figure_dir / "monthly_revenue.png")

    product = (clean.groupby("ProductName", as_index=False)["TotalValue"].sum()
               .sort_values("TotalValue", ascending=False).reset_index(drop=True))
    product.to_csv(export_dir / "product_sales.csv", index=False)
    product_top = product.head(10).iloc[::-1]
    fig, ax = plt.subplots(figsize=(9, 5.2))
    ax.barh(product_top["ProductName"].str.slice(0, 38), product_top["TotalValue"] / 1e6)
    ax.set_xlabel("Revenue (£ millions)")
    ax.set_title("Top 10 Products by Revenue")
    save_plot(figure_dir / "top_products.png")
    product["RevenueShare"] = product["TotalValue"] / product["TotalValue"].sum()
    product["CumulativeShare"] = product["RevenueShare"].cumsum()
    product.rename(columns={"ProductName": "Product"})[["Product", "TotalValue", "RevenueShare", "CumulativeShare"]].to_csv(export_dir / "product_revenue.csv", index=False)
    pd.DataFrame({"ProductRank": np.arange(1, len(product) + 1), "CumulativeShare": product["CumulativeShare"]}).to_csv(export_dir / "product_pareto.csv", index=False)
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.plot(np.arange(1, len(product)+1), 100 * product["CumulativeShare"], linewidth=2)
    ax.axhline(80, linestyle="--", linewidth=1, alpha=0.7)
    ax.set(xlabel="Products ranked by revenue", ylabel="Cumulative revenue share (%)", title="Product Revenue Concentration (Pareto)")
    ax.set_ylim(0, 102)
    ax.grid(axis="y", alpha=0.2)
    save_plot(figure_dir / "product_pareto.png")

    countries = clean.groupby("Country", as_index=False)["TotalValue"].sum().sort_values("TotalValue", ascending=False)
    countries.to_csv(export_dir / "country_sales.csv", index=False)
    fig, ax = plt.subplots(figsize=(9, 4.6))
    country_top = countries.head(9).iloc[::-1]
    ax.barh(country_top["Country"], country_top["TotalValue"] / 1e6)
    ax.set(xlabel="Revenue (£ millions)", title="Top Countries by Revenue")
    save_plot(figure_dir / "country_revenue.png")

    cust = (clean.dropna(subset=["CustomerNo"])
            .groupby("CustomerNo", as_index=False)
            .agg(TotalRevenue=("TotalValue", "sum"), Transactions=("TransactionNo", "nunique")))
    # Replace original (pseudonymous) customer IDs with locally assigned surrogate IDs.
    # Keeps Tableau customer-level charts functional without publishing the source identifiers.
    tableau_customers = cust[["TotalRevenue", "Transactions"]].reset_index(drop=True).copy()
    tableau_customers.insert(0, "CustomerNo", np.arange(1, len(tableau_customers) + 1))
    tableau_customers.to_csv(export_dir / "customer_summary.csv", index=False)
    p25, p75 = cust["TotalRevenue"].quantile([0.25, 0.75]).tolist()
    cust["RevenueSegment"] = np.select([cust["TotalRevenue"] <= p25, cust["TotalRevenue"] <= p75],
                                       ["Low Value", "Medium Value"], default="High Value")
    segment_summary = (cust.groupby("RevenueSegment", as_index=False).agg(
        Customers=("CustomerNo", "size"), MeanRevenue=("TotalRevenue", "mean"), MeanTransactions=("Transactions", "mean")))
    segment_summary.to_csv(export_dir / "revenue_tier_summary.csv", index=False)
    fig, ax = plt.subplots(figsize=(8, 4.4))
    ax.bar(segment_summary["RevenueSegment"], segment_summary["MeanRevenue"])
    ax.set(ylabel="Mean revenue per customer (£)", title="Revenue-Based Customer Tiers (Original Notebook Method)")
    save_plot(figure_dir / "customer_revenue_tiers.png")

    print(f"Processed {len(df):,} lines; valid positive sales lines {len(clean):,}")
    print(f"Revenue: £{total_revenue:,.2f}; Transactions: {transaction_count:,}; Unique known customers: {known_customers:,}")
    print(f"Exports saved to {export_dir} | Figures saved to {figure_dir}")
    return {"rows": len(df), "clean_sales_lines": len(clean), "revenue": total_revenue, "customers": known_customers, "transactions": transaction_count}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, default=Path("data/raw/Sales Transaction v.4a.csv"))
    p.add_argument("--exports", type=Path, default=Path("data/tableau_exports"))
    p.add_argument("--figures", type=Path, default=Path("figures"))
    args = p.parse_args()
    run(args.input, args.exports, args.figures)
