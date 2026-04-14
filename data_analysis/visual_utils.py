# data_analysis/visual_utils.py
"""
Visual utilities leggeri per analisi esplorativa.
Requisiti: pandas, matplotlib, (seaborn opzionale)
Funzioni:
- load_csv
- plot_line
- plot_bar
- plot_hist
- plot_scatter
- plot_corr_heatmap
- save_fig (interno)
"""

from typing import Optional
import pandas as pd
import matplotlib.pyplot as plt

# prova import seaborn ma non obbligatorio
try:
    import seaborn as sns
    _HAS_SEABORN = True
except Exception:
    _HAS_SEABORN = False

# Impostazioni base estetica
plt.style.use("seaborn-darkgrid" if _HAS_SEABORN else "ggplot")

def load_csv(path: str, parse_dates: Optional[list] = None, **kwargs) -> pd.DataFrame:
    """
    Carica un CSV in DataFrame.
    parse_dates: lista di colonne da interpretare come date
    kwargs passati a pd.read_csv
    """
    if parse_dates:
        return pd.read_csv(path, parse_dates=parse_dates, **kwargs)
    return pd.read_csv(path, **kwargs)

def _save_fig(fig: plt.Figure, save_path: Optional[str], dpi: int = 150):
    if save_path:
        fig.savefig(save_path, bbox_inches="tight", dpi=dpi)

def plot_line(df: pd.DataFrame, x: str, y: str, title: Optional[str] = None,
              xlabel: Optional[str] = None, ylabel: Optional[str] = None,
              rotate_xticks: Optional[int] = None, save_path: Optional[str] = None,
              figsize: tuple = (10, 5), **plot_kwargs):
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(df[x], df[y], **plot_kwargs)
    ax.set_title(title or "")
    ax.set_xlabel(xlabel or x)
    ax.set_ylabel(ylabel or y)
    if rotate_xticks:
        plt.setp(ax.get_xticklabels(), rotation=rotate_xticks, ha="right")
    plt.tight_layout()
    _save_fig(fig, save_path)
    plt.show()
    plt.close(fig)

def plot_bar(df: pd.DataFrame, x: str, y: Optional[str] = None, agg: str = "sum",
             title: Optional[str] = None, xlabel: Optional[str] = None,
             ylabel: Optional[str] = None, save_path: Optional[str] = None,
             figsize: tuple = (9, 5), **plot_kwargs):
    """
    If y is provided, groups by x and aggregates y using agg (sum/mean/count).
    If y is None, counts occurrences of x.
    """
    if y:
        if agg not in ("sum", "mean", "count"):
            raise ValueError("agg must be one of 'sum', 'mean', 'count'")
        if agg == "count":
            data = df.groupby(x)[y].count()
        else:
            data = getattr(df.groupby(x)[y], agg)()
    else:
        data = df[x].value_counts()
    fig, ax = plt.subplots(figsize=figsize)
    data.sort_values(ascending=False).plot.bar(ax=ax, **plot_kwargs)
    ax.set_title(title or "")
    ax.set_xlabel(xlabel or x)
    ax.set_ylabel(ylabel or (y if y else "count"))
    plt.tight_layout()
    _save_fig(fig, save_path)
    plt.show()
    plt.close(fig)

def plot_hist(df: pd.DataFrame, column: str, bins: int = 20, title: Optional[str] = None,
              xlabel: Optional[str] = None, ylabel: Optional[str] = "Frequency",
              save_path: Optional[str] = None, figsize: tuple = (8, 5), **plot_kwargs):
    fig, ax = plt.subplots(figsize=figsize)
    ax.hist(df[column].dropna(), bins=bins, **plot_kwargs)
    ax.set_title(title or "")
    ax.set_xlabel(xlabel or column)
    ax.set_ylabel(ylabel)
    plt.tight_layout()
    _save_fig(fig, save_path)
    plt.show()
    plt.close(fig)

def plot_scatter(df: pd.DataFrame, x: str, y: str, hue: Optional[str] = None,
                 title: Optional[str] = None, xlabel: Optional[str] = None,
                 ylabel: Optional[str] = None, save_path: Optional[str] = None,
                 figsize: tuple = (8, 6), **plot_kwargs):
    fig, ax = plt.subplots(figsize=figsize)
    if hue and _HAS_SEABORN:
        sns.scatterplot(data=df, x=x, y=y, hue=hue, ax=ax, **plot_kwargs)
    elif hue:
        groups = df.groupby(hue)
        for name, group in groups:
            ax.scatter(group[x], group[y], label=str(name), **plot_kwargs)
        ax.legend()
    else:
        ax.scatter(df[x], df[y], **plot_kwargs)
    ax.set_title(title or "")
    ax.set_xlabel(xlabel or x)
    ax.set_ylabel(ylabel or y)
    plt.tight_layout()
    _save_fig(fig, save_path)
    plt.show()
    plt.close(fig)

def plot_corr_heatmap(df: pd.DataFrame, title: Optional[str] = None,
                      annot: bool = True, cmap: str = "coolwarm",
                      save_path: Optional[str] = None, figsize: tuple = (8, 6)):
    """
    df: DataFrame con solo colonne numeriche o subset numerico.
    """
    corr = df.corr()
    fig, ax = plt.subplots(figsize=figsize)
    if _HAS_SEABORN:
        sns.heatmap(corr, annot=annot, cmap=cmap, ax=ax)
    else:
        cax = ax.imshow(corr, cmap=cmap, aspect="auto")
        fig.colorbar(cax)
        ax.set_xticks(range(len(corr.columns)))
        ax.set_xticklabels(corr.columns, rotation=45, ha="right")
        ax.set_yticks(range(len(corr.columns)))
        ax.set_yticklabels(corr.columns)
        if annot:
            for (i, j), val in np.ndenumerate(corr.values):
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", color="w")
    ax.set_title(title or "Correlation heatmap")
    plt.tight_layout()
    _save_fig(fig, save_path)
    plt.show()
    plt.close(fig)

