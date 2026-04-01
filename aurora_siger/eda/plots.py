"""Exploratory data analysis visualization functions."""

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def configure_style() -> None:
    """Apply the Aurora SIGER dark plotting theme."""
    sns.set_style("dark", {
        "axes.facecolor": "black",
        "figure.facecolor": "black",
        "grid.color": "#222222",
        "text.color": "white",
        "axes.labelcolor": "white",
        "xtick.color": "white",
        "ytick.color": "white",
    })
    sns.set_context("talk")


def heatmap_plot(data: pd.DataFrame) -> None:
    """Plot a lower-triangular correlation heatmap."""
    plt.figure(figsize=(7.5, 6))
    plt.title("Heatmap of the correlation between variables")
    corr = data.corr()
    # Mask the upper triangle to avoid redundant mirrored values
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=True, fmt=".2f")
    plt.show()


def distribution_plot(data: pd.DataFrame) -> None:
    """Plot histograms with KDE for all columns."""
    n_vars = len(data.columns)
    n_cols = 2
    # Ceiling division to fit all variables into a 2-column grid
    n_rows = (n_vars + n_cols - 1) // n_cols

    plt.figure(figsize=(16, 4 * n_rows))
    for idx, col in enumerate(data.columns, start=1):
        plt.subplot(n_rows, n_cols, idx)
        sns.histplot(data[col], kde=True, bins=25, color="#4C72B0", edgecolor="black")
        plt.title(f"Distribution of {col}", fontsize=12, fontweight="bold")
        plt.xlabel(col)
        plt.ylabel("Frequency")

    plt.suptitle("Feature Distributions", fontsize=18, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()


def boxplot_analysis(data: pd.DataFrame) -> None:
    """Plot boxen plots for all columns."""
    n_vars = len(data.columns)
    n_cols = 3
    n_rows = (n_vars + n_cols - 1) // n_cols

    plt.figure(figsize=(16, 4 * n_rows))
    for idx, col in enumerate(data.columns):
        plt.subplot(n_rows, n_cols, idx + 1)
        sns.boxenplot(x=data[col], color="#4C72B0")
        plt.title(f"{col}", fontsize=12, fontweight="bold")

    plt.suptitle("Feature Distribution Overview", fontsize=18, fontweight="bold")
    plt.tight_layout()
    plt.show()


def pairplot_data(data: pd.DataFrame) -> None:
    """Plot pairwise feature relationships colored by anomaly label."""
    if data.empty:
        print("Dataframe is empty")
        return

    sns.pairplot(data, hue="anomaly", corner=True, palette="coolwarm")
    plt.suptitle("Feature Inter-correlations by Anomaly", y=1.02, fontsize=16)
    plt.show()


def scatter_3d_anomaly(
    data: pd.DataFrame,
    x_axis: str,
    y_axis: str,
    z_axis: str,
) -> None:
    """Plot a 3D scatter colored by anomaly label using Plotly."""
    import plotly.express as px

    if data.empty:
        print("Dataframe is empty.")
        return

    # Validate all required columns exist before building the plot
    required = [x_axis, y_axis, z_axis, "anomaly"]
    for col in required:
        if col not in data.columns:
            print(f"Column '{col}' not found in dataframe.")
            return

    fig = px.scatter_3d(
        data,
        x=x_axis,
        y=y_axis,
        z=z_axis,
        color="anomaly",
        opacity=0.5,
        title=f"3D Anomaly Visualization: {x_axis} vs {y_axis} vs {z_axis}",
    )
    fig.update_layout(
        scene=dict(xaxis_title=x_axis, yaxis_title=y_axis, zaxis_title=z_axis),
        width=900,
        height=700,
        legend_title="Anomaly",
    )
    # Embed as inline HTML so the plot renders in every notebook
    # environment (VS Code, Colab, JupyterLab) without requiring
    # extra extensions or specific Plotly renderers.
    from IPython.display import display, HTML
    display(HTML(fig.to_html(full_html=False, include_plotlyjs="cdn")))
