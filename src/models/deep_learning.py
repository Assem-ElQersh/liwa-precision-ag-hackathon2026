"""Deep learning models for hyperspectral classification."""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import xarray as xr
from typing import Tuple, Dict, Any, Optional
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
import joblib
from pathlib import Path


class SpectralMLP(nn.Module):
    """MLP for spectral classification (from hackathon DL notebook)."""
    
    def __init__(self, n_bands: int, n_classes: int, hidden_units: list = [32, 16], dropout: float = 0.2):
        super().__init__()
        layers = []
        in_features = n_bands
        
        for h in hidden_units:
            layers.append(nn.Linear(in_features, h))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout))
            in_features = h
        
        layers.append(nn.Linear(in_features, n_classes))
        self.network = nn.Sequential(*layers)
    
    def forward(self, x):
        return self.network(x)


def prepare_dl_data(
    cube: xr.DataArray,
    labels: xr.DataArray,
    train_fraction: float = 0.7,
    batch_size: int = 64,
    seed: int = 42
) -> Tuple[DataLoader, DataLoader, np.ndarray, np.ndarray]:
    """Prepare DataLoaders for deep learning."""
    torch.manual_seed(seed)
    np.random.seed(seed)
    
    # Flatten
    if cube.dims[0] == 'band':
        n_bands = cube.sizes['band']
        X = cube.values.transpose(1, 2, 0).reshape(-1, n_bands)
    else:
        n_bands = cube.sizes['band']
        X = cube.values.reshape(-1, n_bands)
    
    y = labels.values.reshape(-1)
    
    # Remove invalid
    valid = np.all(np.isfinite(X), axis=1) & np.isfinite(y) & (y >= 0)
    X = X[valid]
    y = y[valid]
    
    # Train/test split
    n = len(X)
    indices = np.random.permutation(n)
    split = int(n * train_fraction)
    train_idx, test_idx = indices[:split], indices[split:]
    
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    
    # Normalize using train statistics
    mean = X_train.mean(axis=0, keepdims=True)
    std = X_train.std(axis=0, keepdims=True) + 1e-6
    X_train = (X_train - mean) / std
    X_test = (X_test - mean) / std
    
    # Create DataLoaders
    train_ds = TensorDataset(torch.FloatTensor(X_train), torch.LongTensor(y_train))
    test_ds = TensorDataset(torch.FloatTensor(X_test), torch.LongTensor(y_test))
    
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False)
    
    return train_loader, test_loader, mean, std


def train_mlp(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    epochs: int = 50,
    learning_rate: float = 0.001,
    device: str = 'cpu',
    patience: int = 10
) -> Dict[str, list]:
    """Train MLP with early stopping."""
    model = model.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    history = {'train_loss': [], 'val_loss': [], 'val_acc': [], 'val_f1': []}
    best_val_loss = float('inf')
    patience_counter = 0
    
    for epoch in range(epochs):
        # Training
        model.train()
        train_losses = []
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            
            optimizer.zero_grad()
            outputs = model(X_batch)
            loss = criterion(outputs, y_batch)
            loss.backward()
            optimizer.step()
            
            train_losses.append(loss.item())
        
        # Validation
        model.eval()
        val_losses = []
        all_preds = []
        all_targets = []
        
        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                X_batch, y_batch = X_batch.to(device), y_batch.to(device)
                outputs = model(X_batch)
                loss = criterion(outputs, y_batch)
                val_losses.append(loss.item())
                
                preds = outputs.argmax(dim=1)
                all_preds.extend(preds.cpu().numpy())
                all_targets.extend(y_batch.cpu().numpy())
        
        history['train_loss'].append(np.mean(train_losses))
        history['val_loss'].append(np.mean(val_losses))
        history['val_acc'].append(accuracy_score(all_targets, all_preds))
        history['val_f1'].append(f1_score(all_targets, all_preds, average='macro'))
        
        # Early stopping
        if history['val_loss'][-1] < best_val_loss:
            best_val_loss = history['val_loss'][-1]
            patience_counter = 0
            best_state = model.state_dict().copy()
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"Early stopping at epoch {epoch+1}")
                model.load_state_dict(best_state)
                break
        
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}: train_loss={history['train_loss'][-1]:.4f}, "
                  f"val_loss={history['val_loss'][-1]:.4f}, "
                  f"val_acc={history['val_acc'][-1]:.4f}, "
                  f"val_f1={history['val_f1'][-1]:.4f}")
    
    return history


def evaluate_mlp(
    model: nn.Module,
    test_loader: DataLoader,
    device: str = 'cpu'
) -> Dict[str, Any]:
    """Evaluate trained MLP."""
    model.eval()
    model = model.to(device)
    
    all_preds = []
    all_targets = []
    
    with torch.no_grad():
        for X_batch, y_batch in test_loader:
            X_batch = X_batch.to(device)
            outputs = model(X_batch)
            preds = outputs.argmax(dim=1)
            all_preds.extend(preds.cpu().numpy())
            all_targets.extend(y_batch.numpy())
    
    return {
        'accuracy': accuracy_score(all_targets, all_preds),
        'macro_f1': f1_score(all_targets, all_preds, average='macro'),
        'weighted_f1': f1_score(all_targets, all_preds, average='weighted'),
        'confusion_matrix': confusion_matrix(all_targets, all_preds).tolist(),
        'predictions': all_preds,
        'targets': all_targets
    }


def predict_map_dl(
    model: nn.Module,
    cube: xr.DataArray,
    mean: np.ndarray,
    std: np.ndarray,
    device: str = 'cpu',
    batch_size: int = 4096
) -> np.ndarray:
    """Generate prediction map from trained MLP."""
    model.eval()
    model = model.to(device)
    
    if cube.dims[0] == 'band':
        n_bands = cube.sizes['band']
        h, w = cube.sizes['y'], cube.sizes['x']
        X = cube.values.transpose(1, 2, 0).reshape(-1, n_bands)
    else:
        n_bands = cube.sizes['band']
        h, w = cube.sizes['y'], cube.sizes['x']
        X = cube.values.reshape(-1, n_bands)
    
    # Normalize
    X = (X - mean) / std
    
    # Handle NaN
    valid = np.all(np.isfinite(X), axis=1)
    X_valid = X[valid]
    
    # Predict in batches
    preds = np.full(X.shape[0], -1, dtype=np.int32)
    
    with torch.no_grad():
        for i in range(0, len(X_valid), batch_size):
            batch = torch.FloatTensor(X_valid[i:i+batch_size]).to(device)
            outputs = model(batch)
            batch_preds = outputs.argmax(dim=1).cpu().numpy()
            preds[valid][i:i+batch_size] = batch_preds
    
    return preds.reshape(h, w)


def save_dl_model(model: nn.Module, mean: np.ndarray, std: np.ndarray, path: str):
    """Save DL model with preprocessing parameters."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    torch.save({
        'model_state_dict': model.state_dict(),
        'mean': mean,
        'std': std,
        'model_class': model.__class__.__name__,
    }, path)


def load_dl_model(model_class, path: str, device: str = 'cpu'):
    """Load DL model with preprocessing parameters."""
    checkpoint = torch.load(path, map_location=device)
    model = model_class()
    model.load_state_dict(checkpoint['model_state_dict'])
    return model, checkpoint['mean'], checkpoint['std']
