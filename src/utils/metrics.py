"""Metrics and validation utilities."""
import numpy as np
import xarray as xr
from typing import Tuple, Dict, List
from sklearn.metrics import (
    accuracy_score, f1_score, confusion_matrix,
    classification_report, precision_score, recall_score
)
from sklearn.model_selection import KFold


def compute_classification_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    class_names: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Compute comprehensive classification metrics."""
    metrics = {
        'accuracy': accuracy_score(y_true, y_pred),
        'macro_f1': f1_score(y_true, y_pred, average='macro'),
        'micro_f1': f1_score(y_true, y_pred, average='micro'),
        'weighted_f1': f1_score(y_true, y_pred, average='weighted'),
        'macro_precision': precision_score(y_true, y_pred, average='macro', zero_division=0),
        'macro_recall': recall_score(y_true, y_pred, average='macro', zero_division=0),
        'confusion_matrix': confusion_matrix(y_true, y_pred).tolist(),
    }
    
    if class_names:
        metrics['classification_report'] = classification_report(
            y_true, y_pred, target_names=class_names, output_dict=True, zero_division=0
        )
        metrics['per_class_f1'] = f1_score(y_true, y_pred, average=None, zero_division=0).tolist()
        if class_names:
            metrics['per_class_f1_dict'] = dict(zip(class_names, metrics['per_class_f1']))
    
    return metrics


def spatial_cv_split(
    indices: xr.DataArray,
    labels: xr.DataArray,
    n_splits: int = 5,
    block_size: int = 24,
    buffer: int = 2
) -> List[Tuple[np.ndarray, np.ndarray]]:
    """
    Create spatial cross-validation splits using block-based approach.
    Based on hackathon DL notebook methodology.
    """
    h, w = indices.sizes['y'], indices.sizes['x']
    
    # Create fold assignment
    row, col = np.indices((h, w))
    fold = (row // block_size + 2 * (col // block_size)) % n_splits
    
    # Buffer zones
    margin = ((row % block_size < buffer) |
              (row % block_size >= block_size - buffer) |
              (col % block_size < buffer) |
              (col % block_size >= block_size - buffer))
    fold[margin] = -1  # Exclude buffer
    
    # Valid labels only
    valid_labels = labels.values >= 0
    fold[~valid_labels] = -1
    
    splits = []
    for i in range(n_splits):
        train_mask = (fold != i) & (fold >= 0)
        test_mask = (fold == i)
        
        train_idx = np.where(train_mask.ravel())[0]
        test_idx = np.where(test_mask.ravel())[0]
        
        splits.append((train_idx, test_idx))
    
    return splits


def compute_regression_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray
) -> Dict[str, float]:
    """Compute regression metrics."""
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    
    return {
        'mae': mean_absolute_error(y_true, y_pred),
        'mse': mean_squared_error(y_true, y_pred),
        'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
        'r2': r2_score(y_true, y_pred),
    }
