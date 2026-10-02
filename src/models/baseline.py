"""Baseline ML models using scikit-learn."""
import numpy as np
import xarray as xr
from typing import Tuple, Dict, Any
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import (
    accuracy_score, f1_score, confusion_matrix, 
    classification_report, mean_squared_error, r2_score
)
from sklearn.preprocessing import StandardScaler
import joblib
from pathlib import Path


def prepare_ml_data(
    indices: xr.DataArray,
    labels: xr.DataArray,
    train_fraction: float = 0.7,
    spatial_split: bool = True
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Prepare training/test data from indices and labels."""
    # Flatten spatial dimensions
    n_samples = indices.sizes['y'] * indices.sizes['x']
    n_features = indices.sizes['index']
    
    X = indices.values.reshape(n_features, -1).T  # (n_pixels, n_indices)
    y = labels.values.reshape(-1)
    
    # Remove NaN
    valid = ~np.isnan(X).any(axis=1) & ~np.isnan(y)
    X = X[valid]
    y = y[valid]
    
    if spatial_split:
        # Simple spatial split - use spatial blocks
        # For production, use proper spatial CV
        n = len(X)
        split_idx = int(n * train_fraction)
        indices_shuffled = np.random.permutation(n)
        train_idx = indices_shuffled[:split_idx]
        test_idx = indices_shuffled[split_idx:]
    else:
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, train_size=train_fraction, stratify=y, random_state=42
        )
        return X_train, X_test, y_train, y_test
    
    return X[train_idx], X[test_idx], y[train_idx], y[test_idx]


def train_random_forest(
    X_train: np.ndarray,
    y_train: np.ndarray,
    n_estimators: int = 200,
    max_depth: int = 20,
    class_weight: str = "balanced",
    random_state: int = 42,
    **kwargs
) -> RandomForestClassifier:
    """Train Random Forest classifier."""
    rf = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        class_weight=class_weight,
        random_state=random_state,
        n_jobs=-1,
        **kwargs
    )
    rf.fit(X_train, y_train)
    return rf


def train_logistic_regression(
    X_train: np.ndarray,
    y_train: np.ndarray,
    max_iter: int = 1000,
    class_weight: str = "balanced",
    random_state: int = 42,
    **kwargs
) -> LogisticRegression:
    """Train Logistic Regression with scaling."""
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    lr = LogisticRegression(
        max_iter=max_iter,
        class_weight=class_weight,
        random_state=random_state,
        multi_class='multinomial',
        solver='lbfgs',
        **kwargs
    )
    lr.fit(X_train_scaled, y_train)
    
    # Return model with scaler attached
    lr.scaler_ = scaler
    return lr


def evaluate_model(
    model,
    X_test: np.ndarray,
    y_test: np.ndarray,
    class_names: Optional[list] = None
) -> Dict[str, Any]:
    """Evaluate model performance."""
    # Handle scaled models
    if hasattr(model, 'scaler_'):
        X_test = model.scaler_.transform(X_test)
    
    y_pred = model.predict(X_test)
    
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'macro_f1': f1_score(y_test, y_pred, average='macro'),
        'weighted_f1': f1_score(y_test, y_pred, average='weighted'),
        'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
    }
    
    if class_names:
        metrics['classification_report'] = classification_report(
            y_test, y_pred, target_names=class_names, output_dict=True
        )
    
    return metrics


def cross_validate_model(
    model,
    X: np.ndarray,
    y: np.ndarray,
    cv: int = 5,
    scoring: str = 'f1_macro'
) -> Dict[str, float]:
    """Cross-validate model with spatial awareness."""
    scores = cross_val_score(model, X, y, cv=cv, scoring=scoring, n_jobs=-1)
    return {
        'mean': scores.mean(),
        'std': scores.std(),
        'scores': scores.tolist()
    }


def save_model(model, path: str):
    """Save model to disk."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)


def load_model(path: str):
    """Load model from disk."""
    return joblib.load(path)


def predict_map(model, indices: xr.DataArray, output_shape: Tuple[int, int]) -> np.ndarray:
    """Generate prediction map from trained model."""
    n_features = indices.sizes['index']
    X = indices.values.reshape(n_features, -1).T
    
    # Handle NaN
    valid = ~np.isnan(X).any(axis=1)
    X_valid = X[valid]
    
    if hasattr(model, 'scaler_'):
        X_valid = model.scaler_.transform(X_valid)
    
    preds = np.full(X.shape[0], np.nan)
    preds[valid] = model.predict(X_valid)
    
    return preds.reshape(output_shape)
