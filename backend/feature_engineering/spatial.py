import numpy as np


EARTH_RADIUS_M = 6371008.8


def haversine_distances_m(latitude, longitude, facilities):
    if facilities.empty:
        return np.array([])

    event_point = np.radians([latitude, longitude])
    facility_points = np.radians(
        facilities[["latitude", "longitude"]].to_numpy()
    )

    delta = facility_points - event_point
    a = (
        np.sin(delta[:, 0] / 2) ** 2
        + np.cos(event_point[0])
        * np.cos(facility_points[:, 0])
        * np.sin(delta[:, 1] / 2) ** 2
    )

    return 2 * EARTH_RADIUS_M * np.arcsin(np.sqrt(a))


def calculate_spatial_features(event, facilities):
    distances = haversine_distances_m(
        event["latitude"],
        event["longitude"],
        facilities,
    )

    if not len(distances):
        nearest_distance = None
        within_1km = 0
        within_5km = 0
    else:
        nearest_distance = float(distances.min())
        within_1km = int((distances <= 1000).sum())
        within_5km = int((distances <= 5000).sum())

    return {
        "facility_distance_m": nearest_distance,
        "facilities_within_1km": within_1km,
        "facilities_within_5km": within_5km,
    }
