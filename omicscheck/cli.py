import typer
from rich.progress import Progress
from pathlib import Path
from omicscheck import (
    download_series_matrix,
    parse_series_matrix,
    analyze_expression_matrix,
    plot_boxplot,
    plot_heatmap,
    generate_pdf_report,
)
from omicscheck.utils import get_output_path
from omicscheck.visualizer import plot_heatmap_top_genes
import pandas as pd
import logging
import os
import numpy as np
"""
Multi Formats!!
"""
SUPPORTED_EXTENSIONS = [".txt", ".csv", ".tsv", ".xlsx", ".soft", ".gz"]


def setup_logger(gse_id: str, output_dir: Path) -> logging.Logger:
    logger = logging.getLogger(gse_id)
    logger.setLevel(logging.INFO)

    # Remove existing handlers
    logger.handlers.clear()

    # Create log file in output directory on Desktop
    log_path = output_dir / "run.log"
    fh = logging.FileHandler(log_path)
    fh.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


app = typer.Typer()

def auto_orient_dataframe(df: pd.DataFrame, logger) -> tuple[pd.DataFrame, str]:
    """
    Detects if genes are in columns instead of rows and transposes the DataFrame if needed.
    Returns the (possibly transposed) DataFrame and an orientation note string.
    """
    if df.shape[0] < df.shape[1]:
        try:
            numeric_count = pd.to_numeric(df.columns[:5], errors='coerce').notna().sum()
            if numeric_count >= 3:
                logger.info("Orientation check complete. Transposed matrix.")
                return df.T, "Matrix was transposed automatically."
        except Exception:
            logger.info("Orientation check encountered an issue. Transposed matrix by default.")
            return df.T, "Matrix was transposed due to parsing issue."
    return df, "Matrix orientation was correct."

def suggest_log2_transform(df: pd.DataFrame, logger) -> str:
    """
    Suggest log2 transformation if data is highly skewed or contains extreme values.
    Returns a message with the recommendation.
    """
    values = df.values.flatten()
    finite_vals = values[np.isfinite(values)]

    if np.nanmax(finite_vals) > 1000:
        logger.info("Suggested log2 transformation: max value > 1000.")
        return "Log2 transformation is recommended due to high expression values."
    if pd.DataFrame(finite_vals).skew(axis=None, skipna=True).item() > 2:
        logger.info("Suggested log2 transformation: data is highly skewed.")
        return "Log2 transformation is recommended due to data skewness."

    return "No transformation applied"

def filter_variable_genes(df: pd.DataFrame, top_n: int = 1000, logger=None) -> pd.DataFrame:
    """
    Filters the top N most variable genes based on variance.
    """
    variances = df.var(axis=1)
    top_genes = variances.sort_values(ascending=False).head(top_n).index
    filtered_df = df.loc[top_genes]
    if logger:
        logger.info(f"Filtered top {top_n} variable genes from matrix of shape {df.shape} → {filtered_df.shape}")
    return filtered_df

@app.command()
def run(gse_id: str):
    """
    Run OmicsCheck analysis on a given GEO Series ID (e.g., GSE12345).
    """
    typer.echo(f"🔍 Starting OmicsCheck for {gse_id}...\n")

    output_dir = get_output_path(gse_id)
    logger = setup_logger(gse_id, output_dir)
    logger.info(f"Starting OmicsCheck for {gse_id}")

    with Progress() as progress:
        task = progress.add_task("Running analysis...", total=6)

        try:
            progress.update(task, description="📥 Downloading file", advance=1)
            buffer = download_series_matrix(gse_id)
            logger.info("File downloaded successfully.")

            progress.update(task, description="📂 Parsing matrix", advance=1)
            df = parse_series_matrix(buffer)
            df, orientation_note = auto_orient_dataframe(df, logger)
            logger.info(f"Parsed matrix with shape: {df.shape}")

            log2_note = suggest_log2_transform(df, logger)
            df = filter_variable_genes(df, top_n=1000, logger=logger)

            progress.update(task, description="📈 Analyzing data", advance=1)
            analysis = analyze_expression_matrix(df)
            logger.info("Analysis complete.")

            progress.update(task, description="📊 Plotting charts", advance=1)
            plot_boxplot(df, output_dir)
            plot_heatmap(df, output_dir)
            plot_heatmap_top_genes(df, output_dir, top_n=100)
            logger.info("Plots generated.")

            progress.update(task, description="📝 Generating PDF", advance=1)
            generate_pdf_report(gse_id, analysis, output_dir, orientation_note, log2_note)
            logger.info("PDF report generated.")

            typer.echo(f"\n✅ Done! Report saved to: {output_dir / 'report.pdf'}")
            logger.info("OmicsCheck finished successfully.")

        except Exception as e:
            typer.echo(f"\n❌ Error: {e}")
            logger.error(f"Error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    app()
