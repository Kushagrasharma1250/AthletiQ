import argparse
import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from shapely.geometry import LineString, Point, Polygon
from sqlalchemy import create_engine, text


load_dotenv(Path(__file__).parents[2] / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
OVERPASS_URL = os.getenv(
    "OVERPASS_URL",
    "https://overpass-api.de/api/interpreter"
)
OSM_USER_AGENT = os.getenv(
    "OSM_USER_AGENT",
    "AthletiQ/1.0 (geospatial research prototype)"
)
CACHE_DIR = Path(__file__).parents[2] / "data" / "raw" / "osm"

FEATURE_QUERIES = """
(
  nwr["landuse"="industrial"]({south},{west},{north},{east});
  nwr["industrial"]({south},{west},{north},{east});
  nwr["power"~"plant|substation"]({south},{west},{north},{east});
  nwr["highway"]({south},{west},{north},{east});
  nwr["building"]({south},{west},{north},{east});
  nwr["landuse"~"quarry|mine"]({south},{west},{north},{east});
  nwr["amenity"="fuel"]({south},{west},{north},{east});
  nwr["man_made"~"storage_tank|works"]({south},{west},{north},{east});
);
out geom tags;
"""


def build_query(south, west, north, east):
    return "[out:json][timeout:180];" + FEATURE_QUERIES.format(
        south=south,
        west=west,
        north=north,
        east=east,
    )


def fetch_overpass(south, west, north, east, cache_path=None):
    if cache_path and cache_path.exists():
        return json.loads(cache_path.read_text(encoding="utf-8"))

    response = requests.post(
        OVERPASS_URL,
        data=build_query(south, west, north, east),
        headers={"User-Agent": OSM_USER_AGENT},
        timeout=240,
    )
    response.raise_for_status()
    data = response.json()

    if cache_path:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(
            json.dumps(data),
            encoding="utf-8"
        )

    return data


def element_geometry(element):
    if element.get("type") == "node":
        return Point(element["lon"], element["lat"])

    coordinates = [
        (point["lon"], point["lat"])
        for point in element.get("geometry", [])
    ]
    if len(coordinates) < 2:
        return None

    if coordinates[0] == coordinates[-1] and len(coordinates) >= 4:
        return Polygon(coordinates)
    return LineString(coordinates)


def feature_type(tags):
    for key in (
        "landuse",
        "industrial",
        "power",
        "highway",
        "building",
        "amenity",
        "man_made",
    ):
        if tags.get(key):
            return f"{key}:{tags[key]}"
    return "osm_feature"


def parse_elements(data):
    features = []
    for element in data.get("elements", []):
        geometry = element_geometry(element)
        if geometry is None:
            continue

        tags = element.get("tags", {})
        features.append(
            {
                "osm_id": element["id"],
                "osm_type": element["type"],
                "feature_type": feature_type(tags),
                "name": tags.get("name"),
                "tags": json.dumps(tags),
                "wkt": geometry.wkt,
            }
        )
    return features


def store_features(features, engine):
    query = text(
        """
        INSERT INTO osm_features
            (osm_id, osm_type, feature_type, name, tags, geometry, source)
        VALUES
            (:osm_id, :osm_type, :feature_type, :name, CAST(:tags AS JSONB),
             ST_SetSRID(ST_GeomFromText(:wkt), 4326), 'overpass')
        ON CONFLICT (osm_type, osm_id) DO UPDATE SET
            feature_type = EXCLUDED.feature_type,
            name = EXCLUDED.name,
            tags = EXCLUDED.tags,
            geometry = EXCLUDED.geometry,
            updated_at = CURRENT_TIMESTAMP;
        """
    )
    with engine.begin() as connection:
        connection.execute(query, features)


def ingest(south, west, north, east, cache_path=None):
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is missing from .env")

    data = fetch_overpass(south, west, north, east, cache_path)
    features = parse_elements(data)
    if features:
        store_features(features, create_engine(DATABASE_URL, pool_pre_ping=True))
    return len(features)


def main():
    parser = argparse.ArgumentParser(description="Import OSM features via Overpass")
    parser.add_argument("--south", type=float, required=True)
    parser.add_argument("--west", type=float, required=True)
    parser.add_argument("--north", type=float, required=True)
    parser.add_argument("--east", type=float, required=True)
    parser.add_argument("--cache", type=Path)
    args = parser.parse_args()
    count = ingest(
        args.south,
        args.west,
        args.north,
        args.east,
        args.cache,
    )
    print(f"OSM features ingested: {count}")


if __name__ == "__main__":
    main()