import pandas as pd
import numpy as np


INPUT_FILE = r"C:\Users\ssk12\OneDrive\Documents\GitHub\AthletiQ\backend\data\processed\training.csv"
OUTPUT_FILE = r"C:\Users\ssk12\OneDrive\Documents\GitHub\AthletiQ\backend\data\processed\training_with_recurrence.csv"


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

RECURRENCE_RADIUS_KM = 5.0


# ---------------------------------------------------------
# Haversine distance
# ---------------------------------------------------------

def haversine_distance(
    lat1,
    lon1,
    lat2,
    lon2
):

    R = 6371.0

    lat1 = np.radians(lat1)
    lat2 = np.radians(lat2)

    dlat = lat2 - lat1
    dlon = np.radians(lon2) - np.radians(lon1)

    a = (
        np.sin(dlat / 2) ** 2
        +
        np.cos(lat1)
        * np.cos(lat2)
        * np.sin(dlon / 2) ** 2
    )

    return (
        2
        * R
        * np.arcsin(np.sqrt(a))
    )


# ---------------------------------------------------------
# Calculate recurrence
# ---------------------------------------------------------

def calculate_recurrence(df):

    df = df.copy()

    df["event_date"] = pd.to_datetime(
        df["event_date"]
    )


    recurrence = []


    for i, current in df.iterrows():

        current_lat = current["latitude"]
        current_lon = current["longitude"]
        current_date = current["event_date"]


        count = 0


        for j, previous in df.iterrows():

            # Don't compare the event with itself

            if i == j:
                continue


            previous_date = previous["event_date"]


            # Only count previous events

            if previous_date >= current_date:
                continue


            distance = haversine_distance(

                current_lat,
                current_lon,

                previous["latitude"],
                previous["longitude"]

            )


            if distance <= RECURRENCE_RADIUS_KM:

                count += 1


        recurrence.append(count)


    df["recurrence_frequency"] = recurrence


    return df


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    print(
        "Loading training dataset..."
    )


    df = pd.read_csv(
        INPUT_FILE
    )


    print(
        f"Events loaded: {len(df)}"
    )


    required_columns = [

        "event_id",
        "latitude",
        "longitude",
        "event_date",

        "frp_mean",
        "frp_max",
        "confidence",

        "facility_distance",
        "facility_count",

        "industrial_ratio",
        "forest_ratio",
        "agriculture_ratio",
        "builtup_ratio",

        "detection_count",
        "event_duration_hours",

        "label"

    ]


    missing = [

        column
        for column in required_columns
        if column not in df.columns

    ]


    if missing:

        raise ValueError(
            f"Missing columns: {missing}"
        )


    df = calculate_recurrence(
        df
    )


    df.to_csv(
        OUTPUT_FILE,
        index=False
    )


    print(
        "\nRecurrence calculated."
    )


    print(
        df[
            [
                "event_id",
                "event_date",
                "recurrence_frequency",
                "label"
            ]
        ].to_string(index=False)
    )


    print(
        f"\nSaved to: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()