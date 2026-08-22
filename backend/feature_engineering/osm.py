import numpy as np
from shapely import wkt
from shapely.geometry import Point


EARTH_RADIUS_M = 6371008.8


def _distances_m(event, features):
    if features.empty:
        return np.array([])

    event_point = np.radians([event["latitude"], event["longitude"]])
    feature_points = np.radians(
        features[["latitude", "longitude"]].to_numpy()
    )
    delta = feature_points - event_point
    a = (
        np.sin(delta[:, 0] / 2) ** 2
        + np.cos(event_point[0])
        * np.cos(feature_points[:, 0])
        * np.sin(delta[:, 1] / 2) ** 2
    )
    return 2 * EARTH_RADIUS_M * np.arcsin(np.sqrt(a))


def _subset(features, prefixes):
    return features[
        features["feature_type"].str.startswith(tuple(prefixes))
    ]


def _nearest_distance(event, features):
    distances = _distances_m(event, features)
    return None if not len(distances) else float(distances.min())


def _count_within(event, features, radius_m):
    distances = _distances_m(event, features)
    return int((distances <= radius_m).sum()) if len(distances) else 0


def calculate_osm_features(event, osm_features):
    if not osm_features.empty:
        latitude = event["latitude"]
        longitude = event["longitude"]
        osm_features = osm_features[
            osm_features["latitude"].between(latitude - 0.1, latitude + 0.1)
            & osm_features["longitude"].between(longitude - 0.1, longitude + 0.1)
        ]

    industrial = _subset(osm_features, ("landuse:industrial", "industrial:"))
    roads = _subset(osm_features, ("highway:",))
    buildings = _subset(osm_features, ("building:",))
    power_plants = _subset(osm_features, ("power:plant",))
    substations = _subset(osm_features, ("power:substation",))
    mines = _subset(osm_features, ("landuse:mine", "industrial:mine"))
    quarries = _subset(osm_features, ("landuse:quarry",))
    event_buffer = Point(
        event["longitude"],
        event["latitude"],
    ).buffer(1000 / 111320)
    industrial_polygons = [
        wkt.loads(value)
        for value in industrial["geometry_wkt"].dropna()
        if wkt.loads(value).geom_type in ("Polygon", "MultiPolygon")
    ]
    industrial_area = sum(
        polygon.intersection(event_buffer).area
        for polygon in industrial_polygons
    )

    primary_roads = roads[
        roads["feature_type"].isin(
            ["highway:motorway", "highway:trunk", "highway:primary"]
        )
    ]

    return {
        "osm_industrial_distance_m": _nearest_distance(event, industrial),
        "osm_industrial_count": _count_within(event, industrial, 5000),
        "osm_industrial_area_ratio": min(
            industrial_area / event_buffer.area,
            1.0,
        ),
        "osm_road_distance_m": _nearest_distance(event, roads),
        "osm_primary_road_distance_m": _nearest_distance(event, primary_roads),
        "osm_building_count_500m": _count_within(event, buildings, 500),
        "osm_building_density_500m": (
            _count_within(event, buildings, 500) / (np.pi * 0.5 ** 2)
        ),
        "osm_powerplant_distance_m": _nearest_distance(event, power_plants),
        "osm_substation_distance_m": _nearest_distance(event, substations),
        "osm_mine_distance_m": _nearest_distance(event, mines),
        "osm_quarry_distance_m": _nearest_distance(event, quarries),
    }