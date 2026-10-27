"""POST-THESIS PORTFOLIO EXTENSION: independent implementation of RFM K-means.

The provided original notebook computed revenue quantile groups, not the
full recency/frequency/monetary K-means procedure discussed in the thesis.
This extension implements that separate analysis and does not claim to
reproduce the thesis's published cluster numbers exactly.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from run_analysis import load_transactions


def run(input_path: Path, out_dir: Path, figures: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    df = load_transactions(input_path)
    valid = (df["Quantity"] > 0) & (df["Price"] > 0) & ~df["TransactionNo"].fillna("").str.startswith("C") & df["Date"].notna() & df["CustomerNo"].notna()
    df = df.loc[valid].copy()
    ref_date = df["Date"].max() + pd.Timedelta(days=1)
    rfm = (df.groupby("CustomerNo").agg(
        LastPurchase=("Date", "max"), Frequency=("TransactionNo", "nunique"), Monetary=("TotalValue", "sum")))
    rfm["Recency"] = (ref_date - rfm["LastPurchase"]).dt.days
    rfm = rfm[(rfm["Frequency"] > 0) & (rfm["Monetary"] > 0)]
    # Log transforms limit skew; z-scoring balances feature influence.
    X = pd.DataFrame({"Recency": np.log1p(rfm["Recency"]),
                      "Frequency": np.log1p(rfm["Frequency"]),
                      "Monetary": np.log1p(rfm["Monetary"])}, index=rfm.index)
    scaled = StandardScaler().fit_transform(X)
    model = KMeans(n_clusters=4, n_init=10, random_state=42)
    rfm["Cluster"] = model.fit_predict(scaled)
    summary = (rfm.groupby("Cluster").agg(Customers=("Recency", "size"),
        MeanRecencyDays=("Recency", "mean"), MeanFrequency=("Frequency", "mean"),
        MeanMonetaryGBP=("Monetary", "mean")).reset_index())
    summary.to_csv(out_dir / "rfm_cluster_summary_EXTENSION.csv", index=False)
    fig, ax = plt.subplots(figsize=(8.5, 5))
    scatter = ax.scatter(rfm["Frequency"], rfm["Monetary"], c=rfm["Cluster"], s=9, alpha=0.4)
    ax.set(xlabel="Distinct transactions", ylabel="Monetary (£)", title="RFM K-means Segments (Post-thesis Extension)")
    ax.legend(*scatter.legend_elements(), title="Cluster", loc="best")
    fig.tight_layout()
    fig.savefig(figures / "rfm_clustering_EXTENSION.png", dpi=160)
    plt.close(fig)
    print(summary.to_string(index=False))
    print("Extension: cluster IDs are arbitrary and differ from thesis reported values.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("data/raw/Sales Transaction v.4a.csv"))
    parser.add_argument("--exports", type=Path, default=Path("data/tableau_exports"))
    parser.add_argument("--figures", type=Path, default=Path("figures"))
    args = parser.parse_args()
    run(args.input, args.exports, args.figures)
