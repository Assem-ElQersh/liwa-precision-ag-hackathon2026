"""STAC client for satellite data search."""
import planetary_computer as pc
from pystac_client import Client
from typing import List, Dict, Optional

# Catalog endpoints
PLANETARY_COMPUTER = "https://planetarycomputer.microsoft.com/api/stac/v1"
ENMAP_STAC = "https://enmap.geoservice.dlr.de/stac"
PLANET_TANAGER = "https://stac.planet.com/tanager/open"

# Collections
SENTINEL2_L2A = "sentinel-2-l2a"
LANDSAT_C2_L2 = "landsat-c2-l2"
ENMAP_COLLECTION = "enmap"
TANAGER_COLLECTION = "tanager"


def get_pc_catalog():
    """Get signed Planetary Computer catalog."""
    return Client.open(PLANETARY_COMPUTER, modifier=pc.sign_inplace)


def search_sentinel2(
    bbox: List[float],
    timerange: str,
    max_cloud: int = 30,
    max_items: int = 50
) -> List[Dict]:
    """Search Sentinel-2 L2A on Planetary Computer."""
    catalog = get_pc_catalog()
    search = catalog.search(
        collections=[SENTINEL2_L2A],
        bbox=bbox,
        datetime=timerange,
        query={"eo:cloud_cover": {"lt": max_cloud}},
        max_items=max_items
    )
    items = list(search.items())
    items.sort(key=lambda x: x.datetime)
    return items


def search_landsat(
    bbox: List[float],
    timerange: str,
    max_cloud: int = 30,
    max_items: int = 50
) -> List[Dict]:
    """Search Landsat Collection 2 Level-2 on Planetary Computer."""
    catalog = get_pc_catalog()
    search = catalog.search(
        collections=[LANDSAT_C2_L2],
        bbox=bbox,
        datetime=timerange,
        query={"eo:cloud_cover": {"lt": max_cloud}},
        max_items=max_items
    )
    items = list(search.items())
    items.sort(key=lambda x: x.datetime)
    return items


def search_enmap(
    bbox: List[float],
    timerange: str,
    max_items: int = 20
) -> List[Dict]:
    """Search EnMAP hyperspectral data (requires DLR registration)."""
    try:
        catalog = Client.open(ENMAP_STAC)
        search = catalog.search(
            collections=[ENMAP_COLLECTION],
            bbox=bbox,
            datetime=timerange,
            max_items=max_items
        )
        items = list(search.items())
        items.sort(key=lambda x: x.datetime)
        return items
    except Exception as e:
        print(f"EnMAP search requires authentication: {e}")
        return []


def search_tanager(
    bbox: List[float],
    timerange: str,
    max_items: int = 20
) -> List[Dict]:
    """Search Planet Tanager open archive."""
    try:
        catalog = Client.open(PLANET_TANAGER)
        search = catalog.search(
            collections=[TANAGER_COLLECTION],
            bbox=bbox,
            datetime=timerange,
            max_items=max_items
        )
        items = list(search.items())
        items.sort(key=lambda x: x.datetime)
        return items
    except Exception as e:
        print(f"Tanager search: {e}")
        return []


def get_item_assets(item) -> Dict[str, str]:
    """Extract asset hrefs from STAC item."""
    return {k: v.href for k, v in item.assets.items()}


def print_items_summary(items: List[Dict], limit: int = 10):
    """Print human-readable summary of STAC items."""
    print(f"Found {len(items)} scenes")
    for item in items[:limit]:
        cloud = item.properties.get('eo:cloud_cover', 'N/A')
        print(f"  {item.datetime.date()} | cloud: {cloud}% | {item.id}")
