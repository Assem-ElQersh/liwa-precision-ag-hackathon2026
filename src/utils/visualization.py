"""Visualization utilities."""
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import pandas as pd
from typing import Dict, List, Optional, Tuple
from matplotlib.colors import ListedColormap


def plot_index_map(
    index_data: xr.DataArray,
    title: str,
    cmap: str = 'RdYlGn',
    vmin: Optional[float] = None,
    vmax: Optional[float] = None,
    figsize: Tuple[int, int] = (10, 8),
    save_path: Optional[str] = None
):
    """Plot a single index map."""
    plt.figure(figsize=figsize)
    im = plt.imshow(index_data.values, cmap=cmap, vmin=vmin, vmax=vmax)
    plt.colorbar(im, label=title, fraction=0.046, pad=0.04)
    plt.title(title)
    plt.axis('off')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.show()


def plot_indices_grid(
    indices_dict: Dict[str, np.ndarray],
    ncols: int = 3,
    figsize: Tuple[int, int] = (15, 10),
    save_path: Optional[str] = None
):
    """Plot multiple indices in a grid with appropriate colormaps."""
    n = len(indices_dict)
    nrows = (n + ncols - 1) // ncols
    
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
    axes = axes.flatten() if n > 1 else [axes]
    
    for ax, (name, data) in zip(axes, indices_dict.items()):
        # Choose colormap based on index type
        if any(k in name for k in ['NDVI', 'EVI', 'SAVI', 'NDRE', 'GNDVI', 'CI']):
            cmap = 'RdYlGn'
            vmin, vmax = -0.2, 1.0
        elif any(k in name for k in ['NDWI', 'MSI', 'NMDI', 'LSWI', 'MNDWI']):
            cmap = 'BrBG'
            vmin, vmax = -1, 1
        elif any(k in name for k in ['SI', 'BI', 'SRSI', 'CSRI']):
            cmap = 'RdBu_r'
            vmin, vmax = -1, 1
        else:
            cmap = 'viridis'
            vmin, vmax = None, None
        
        im = ax.imshow(data, cmap=cmap, vmin=vmin, vmax=vmax)
        ax.set_title(name)
        ax.axis('off')
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    
    # Hide unused axes
    for ax in axes[n:]:
        ax.axis('off')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.show()


def plot_timeseries(
    ts_dict: Dict[str, pd.Series],
    title: str = "Time Series",
    xlabel: str = "Date",
    ylabel: str = "Value",
    figsize: Tuple[int, int] = (14, 6),
    save_path: Optional[str] = None
):
    """Plot multiple time series."""
    plt.figure(figsize=figsize)
    for name, ts in ts_dict.items():
        plt.plot(ts.index, ts.values, marker='o', label=name, linewidth=2, markersize=4)
    
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.show()


def plot_classification_map(
    class_map: np.ndarray,
    class_names: List[str],
    colors: Optional[List[str]] = None,
    title: str = "Classification Map",
    figsize: Tuple[int, int] = (10, 8),
    save_path: Optional[str] = None
):
    """Plot classification map with discrete colormap."""
    if colors is None:
        colors = ['#D4A03A', '#0E9E74', '#4E85B9', '#7859A6', '#C56452', '#8B4513']
    
    cmap = ListedColormap(colors[:len(class_names)])
    cmap.set_bad('#E3E7E4')
    
    plt.figure(figsize=figsize)
    im = plt.imshow(class_map, cmap=cmap, vmin=0, vmax=len(class_names)-1, interpolation='nearest')
    
    # Create legend
    from matplotlib.patches import Patch
    handles = [Patch(color=colors[i], label=name) for i, name in enumerate(class_names)]
    plt.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=3)
    
    plt.title(title)
    plt.axis('off')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.show()


def plot_confusion_matrix(
    cm: np.ndarray,
    class_names: List[str],
    title: str = "Confusion Matrix",
    normalize: bool = True,
    figsize: Tuple[int, int] = (8, 6),
    save_path: Optional[str] = None
):
    """Plot confusion matrix."""
    if normalize:
        cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True)
        cm_norm = np.nan_to_num(cm_norm)
    else:
        cm_norm = cm
    
    plt.figure(figsize=figsize)
    im = plt.imshow(cm_norm, cmap='Blues', vmin=0, vmax=1 if normalize else None)
    plt.colorbar(im)
    
    # Annotate
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            if normalize:
                text = f'{cm[i,j]}\n({cm_norm[i,j]:.1%})'
            else:
                text = str(cm[i,j])
            plt.text(j, i, text, ha='center', va='center',
                    color='white' if cm_norm[i,j] > 0.5 else 'black')
    
    plt.xticks(range(len(class_names)), class_names, rotation=45, ha='right')
    plt.yticks(range(len(class_names)), class_names)
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title(title)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.show()


def save_figure(fig, path: str, dpi: int = 150):
    """Save figure with consistent settings."""
    fig.savefig(path, dpi=dpi, bbox_inches='tight', facecolor='white')
