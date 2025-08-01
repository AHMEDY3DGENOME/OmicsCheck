import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path

def plot_boxplot(df: pd.DataFrame, out_path: Path):
    """Generate and save a boxplot of gene expression."""
    if df.empty or df.shape[0] == 0 or df.shape[1] == 0:
        print("⚠️ Skipping boxplot: Dataframe is empty.")
        return
    plt.figure(figsize=(10, 4))
    sns.boxplot(data=df, orient='h', fliersize=1, linewidth=0.5)
    plt.tight_layout()
    plt.savefig(out_path / "boxplot.png")
    plt.close()

def plot_heatmap(df: pd.DataFrame, out_path: Path, top_n: int = 30):
    """Generate and save a heatmap for top N variable genes."""
    if df.empty or df.shape[0] == 0 or df.shape[1] == 0:
        print("⚠️ Skipping heatmap: Dataframe is empty.")
        return
    subset = df.var(axis=1).sort_values(ascending=False).head(top_n).index
    heatmap_data = df.loc[subset]
    plt.figure(figsize=(10, 8))
    sns.heatmap(heatmap_data, cmap='viridis')
    plt.tight_layout()
    plt.savefig(out_path / "heatmap.png")
    plt.close()
def plot_heatmap_top_genes(df, output_dir: Path, top_n: int = 100):
    import seaborn as sns
    import matplotlib.pyplot as plt

    # حساب التباين واختيار الجينات الأعلى
    top_genes = df.var(axis=1).sort_values(ascending=False).head(top_n).index
    filtered = df.loc[top_genes]

    plt.figure(figsize=(15, 10))
    sns.heatmap(filtered, cmap="viridis", xticklabels=False)
    plt.title(f"Heatmap of Top {top_n} Variable Genes")
    heatmap_path = output_dir / f"heatmap_top_{top_n}.png"
    plt.savefig(heatmap_path)
    plt.close()
