"""Hyperspectral feature extraction."""
import numpy as np
import xarray as xr
from typing import List, Tuple, Optional
from sklearn.decomposition import NMF
from sklearn.preprocessing import MinMaxScaler


def find_band_idx(wavelengths: np.ndarray, target_nm: float) -> int:
    """Find closest band index to target wavelength."""
    return np.argmin(np.abs(wavelengths - target_nm))


def extract_signatures(
    cube: xr.DataArray,
    wavelengths: np.ndarray,
    coordinates: List[Tuple[int, int]],
    labels: Optional[List[str]] = None
) -> Tuple[np.ndarray, np.ndarray]:
    """Extract spectral signatures at given coordinates."""
    # Ensure cube is (y, x, band)
    if cube.dims[0] == 'band':
        cube = cube.transpose('y', 'x', 'band')
    
    signatures = []
    for y, x in coordinates:
        spec = cube.isel(y=y, x=x).values
        signatures.append(spec)
    
    signatures = np.array(signatures)
    
    if labels is None:
        labels = [f"Pixel ({y},{x})" for y, x in coordinates]
    
    return signatures, wavelengths


def compute_hs_indices(cube: xr.DataArray, wavelengths: np.ndarray) -> dict:
    """Compute hyperspectral indices for agriculture."""
    def fb(target):
        return find_band_idx(wavelengths, target)
    
    # Key wavelengths
    b550 = fb(550)
    b670 = fb(670)
    b700 = fb(700)
    b750 = fb(750)
    b800 = fb(800)
    b900 = fb(900)
    b970 = fb(970)
    b1200 = fb(1200)
    b1240 = fb(1240)
    b1600 = fb(1600)
    b2100 = fb(2100)
    b2200 = fb(2200)
    
    if cube.dims[0] == 'band':
        cube = cube.transpose('y', 'x', 'band')
    
    indices = {}
    
    # Chlorophyll
    indices['MCARI'] = ((cube[..., b750] - cube[..., b670]) - 0.2 * (cube[..., b750] - cube[..., b700])) * (cube[..., b750] / cube[..., b670])
    indices['TCARI'] = 3 * ((cube[..., b700] - cube[..., b670]) - 0.2 * (cube[..., b700] - cube[..., b550]) * (cube[..., b700] / cube[..., b670]))
    
    # Water
    indices['WI_970'] = cube[..., b970] / cube[..., b900]
    indices['NDWI_HS'] = (cube[..., b860] - cube[..., b1240]) / (cube[..., b860] + cube[..., b1240])
    
    # Salinity
    indices['SI'] = (cube[..., b1600] - cube[..., b670]) / (cube[..., b1600] + cube[..., b670])
    indices['BI'] = (cube[..., b1600]**2 + cube[..., b670]**2)**0.5
    indices['SI1'] = cube[..., b1600] / cube[..., b800]
    indices['SI3'] = (cube[..., b2200] - cube[..., b1600]) / (cube[..., b2200] + cube[..., b1600])
    
    return indices


def spectral_unmixing(
    cube: xr.DataArray,
    n_endmembers: int = 4,
    random_state: int = 42
) -> Tuple[xr.DataArray, np.ndarray]:
    """Perform spectral unmixing using NMF."""
    if cube.dims[0] == 'band':
        cube = cube.transpose('y', 'x', 'band')
    
    h, w, b = cube.shape
    pixels = cube.values.reshape(-1, b)
    
    # Remove NaN/inf
    valid_mask = np.all(np.isfinite(pixels), axis=1)
    pixels_valid = pixels[valid_mask]
    
    # Scale for NMF
    scaler = MinMaxScaler()
    pixels_scaled = scaler.fit_transform(pixels_valid)
    
    # NMF
    nmf = NMF(n_components=n_endmembers, random_state=random_state, max_iter=500)
    abundances_scaled = nmf.fit_transform(pixels_scaled)
    endmembers_scaled = nmf.components_
    
    # Reshape abundances
    abundances_full = np.zeros((h * w, n_endmembers))
    abundances_full[valid_mask] = abundances_scaled
    abundances = abundances_full.reshape(h, w, n_endmembers)
    
    # Inverse transform endmembers
    endmembers = scaler.inverse_transform(endmembers_scaled)
    
    # Convert to DataArray
    abundances_da = xr.DataArray(
        abundances,
        dims=['y', 'x', 'endmember'],
        coords={
            'y': cube.coords['y'],
            'x': cube.coords['x'],
            'endmember': [f'EM{i+1}' for i in range(n_endmembers)]
        },
        name='abundances'
    )
    
    return abundances_da, endmembers
