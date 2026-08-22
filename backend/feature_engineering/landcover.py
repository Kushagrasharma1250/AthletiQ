import os
from pathlib import Path

import rasterio
from dotenv import load_dotenv
from pyproj import Transformer
from rasterio.mask import mask
from shapely.geometry import Point, mapping
from shapely.ops import transform


load_dotenv(Path(__file__).parents[1] / ".env")
LANDCOVER_RASTER_PATH = os.getenv("LANDCOVER_RASTER_PATH")
EVENT_BUFFER_M = 1000


def _event_geometry(event, raster_crs):
    geometry = Point(event["longitude"], event["latitude"]).buffer(
        EVENT_BUFFER_M / 111320
    )
    transformer = Transformer.from_crs(
        "EPSG:4326",
        raster_crs,
        always_xy=True,
    )
    return transform(transformer.transform, geometry)


def calculate_landcover_features(event, raster_path=None):
    empty_features = {
        "forest_ratio": None,
        "agriculture_ratio": None,
        "builtup_ratio": None,
    }
    configured_path = raster_path or LANDCOVER_RASTER_PATH
    if not configured_path:
        return empty_features

    path = Path(configured_path)
    if not path.is_absolute():
        path = Path(__file__).parents[1] / path
    if not path.exists():
        return empty_features

    with rasterio.open(path) as raster:
        geometry = _event_geometry(event, raster.crs)
        values, _ = mask(raster, [mapping(geometry)], crop=True)
        pixels = values[0]
        if raster.nodata is not None:
            pixels = pixels[pixels != raster.nodata]
        if not len(pixels):
            return empty_features

    total = len(pixels)
    return {
        "forest_ratio": float((pixels == 10).sum() / total),
        "agriculture_ratio": float((pixels == 40).sum() / total),
        "builtup_ratio": float((pixels == 50).sum() / total),
    }
