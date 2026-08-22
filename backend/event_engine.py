import os
from pathlib import Path

import numpy as np
import pandas as pd

from dotenv import load_dotenv

from sqlalchemy import create_engine, text

from sklearn.cluster import DBSCAN


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv(Path(__file__).parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is missing from .env"
    )


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


# ============================================================
# EVENT ENGINE PARAMETERS
# ============================================================

# Maximum spatial distance between detections
# that may belong to the same physical event.

SPATIAL_RADIUS_KM = 5.0


# Maximum time difference between consecutive
# detections inside an event.

TEMPORAL_WINDOW_HOURS = 24


# DBSCAN minimum number of points.

# We use 1 because a legitimate satellite fire
# event may contain only one detection.

MIN_SAMPLES = 1


# Mean Earth radius in kilometers.

EARTH_RADIUS_KM = 6371.0088


# ============================================================
# LOAD THERMAL DETECTIONS
# ============================================================

def load_detections():

    query = """
        SELECT

            id,

            latitude,

            longitude,

            acquisition_date,

            acquisition_time,

            brightness_temperature,

            background_temperature,

            frp,

            confidence,

            satellite,

            instrument,

            daynight,

            event_id

        FROM thermal_anomalies

        WHERE latitude IS NOT NULL

          AND longitude IS NOT NULL

        ORDER BY
            acquisition_date,
            acquisition_time;
    """

    with engine.connect() as connection:

        df = pd.read_sql(
            text(query),
            connection
        )

    return df


# ============================================================
# BUILD TIMESTAMP
# ============================================================

def build_timestamp(df):

    df = df.copy()

    # FIRMS acquisition time can be:
    #
    # 2046
    # 2008
    #
    # Make sure it always has four digits.

    df["acquisition_time"] = (
        df["acquisition_time"]
        .astype(str)
        .str.replace(
            ".0",
            "",
            regex=False
        )
        .str.zfill(4)
    )

    df["timestamp"] = pd.to_datetime(

        df["acquisition_date"]
        .astype(str)

        + " "

        + df["acquisition_time"].str[:2]

        + ":"

        + df["acquisition_time"].str[2:4],

        errors="coerce"
    )

    return df


# ============================================================
# SPATIAL DBSCAN
# ============================================================

def spatial_clustering(df):

    if df.empty:

        return df


    df = df.copy()


    # Convert lat/lon to radians because
    # DBSCAN will use the Haversine metric.

    coordinates = np.radians(

        df[
            [
                "latitude",
                "longitude"
            ]
        ].values

    )


    # Convert kilometers to radians.

    eps = (
        SPATIAL_RADIUS_KM
        /
        EARTH_RADIUS_KM
    )


    model = DBSCAN(

        eps=eps,

        min_samples=MIN_SAMPLES,

        metric="haversine"

    )


    labels = model.fit_predict(
        coordinates
    )


    df["spatial_cluster"] = labels


    return df


# ============================================================
# TEMPORAL GROUPING
# ============================================================

def temporal_clustering(df):

    if df.empty:

        return df


    df = df.copy()


    df["event_cluster"] = -1


    next_event_cluster = 0


    # Process each spatial cluster independently.

    for spatial_cluster_id in sorted(

        df["spatial_cluster"].unique()

    ):

        spatial_df = (

            df[
                df["spatial_cluster"]
                == spatial_cluster_id
            ]

            .sort_values("timestamp")

        )


        current_event = None

        previous_timestamp = None


        for index, row in spatial_df.iterrows():

            current_timestamp = (
                row["timestamp"]
            )


            # First detection in this
            # spatial cluster.

            if previous_timestamp is None:

                current_event = (
                    next_event_cluster
                )

                next_event_cluster += 1


            else:

                time_difference = (

                    current_timestamp
                    -
                    previous_timestamp

                )


                # Start a new event if
                # the temporal gap is too large.

                if (

                    time_difference.total_seconds()
                    >
                    TEMPORAL_WINDOW_HOURS * 3600

                ):

                    current_event = (
                        next_event_cluster
                    )

                    next_event_cluster += 1


            df.loc[
                index,
                "event_cluster"
            ] = current_event


            previous_timestamp = (
                current_timestamp
            )


    return df


# ============================================================
# EVENT CENTER
# ============================================================

def calculate_event_center(event_df):

    latitude = (
        event_df["latitude"]
        .mean()
    )

    longitude = (
        event_df["longitude"]
        .mean()
    )

    return latitude, longitude


# ============================================================
# EVENT PERSISTENCE
# ============================================================

def determine_persistence(event_df):

    detection_count = len(
        event_df
    )


    first_detected = (
        event_df["timestamp"].min()
    )

    last_detected = (
        event_df["timestamp"].max()
    )


    duration = (
        last_detected
        -
        first_detected
    )


    # Multiple detections over time.

    if detection_count >= 3:

        return "PERSISTENT"


    if duration.total_seconds() >= 12 * 3600:

        return "PERSISTENT"


    if detection_count == 2:

        return "REPEATED"


    return "SINGLE_DETECTION"


# ============================================================
# INITIAL CONFIDENCE
# ============================================================

def calculate_confidence(event_df):

    detection_count = len(
        event_df
    )


    if detection_count >= 5:

        return 0.90


    if detection_count >= 3:

        return 0.75


    if detection_count == 2:

        return 0.60


    return 0.40


# ============================================================
# INITIAL RISK SCORE
# ============================================================

def calculate_risk_score(event_df):

    score = 0.0


    # --------------------------------------------------------
    # Detection count
    # --------------------------------------------------------

    detection_count = len(
        event_df
    )


    score += min(
        detection_count * 10,
        30
    )


    # --------------------------------------------------------
    # FRP
    # --------------------------------------------------------

    if "frp" in event_df.columns:

        mean_frp = (

            event_df["frp"]

            .fillna(0)

            .mean()

        )

        score += min(
            mean_frp,
            30
        )


    # --------------------------------------------------------
    # Brightness temperature
    # --------------------------------------------------------

    if (
        "brightness_temperature"
        in event_df.columns
    ):

        brightness = (

            event_df[
                "brightness_temperature"
            ]

            .fillna(0)

            .mean()

        )


        if brightness >= 330:

            score += 30

        elif brightness >= 310:

            score += 20

        elif brightness >= 300:

            score += 10


    return min(
        round(score, 2),
        100
    )


# ============================================================
# RISK LEVEL
# ============================================================

def determine_risk_level(score):

    if score >= 75:

        return "HIGH"


    if score >= 50:

        return "MEDIUM"


    return "LOW"


# ============================================================
# GENERATE EVENT CODE
# ============================================================

def generate_event_code(number):

    return f"EVENT-{number:04d}"


def next_event_number():

    query = text(
        """
        SELECT COALESCE(
            MAX(CAST(SUBSTRING(event_code FROM 7) AS INTEGER)),
            0
        ) + 1
        FROM events
        WHERE event_code ~ '^EVENT-[0-9]+$';
        """
    )

    with engine.connect() as connection:
        return int(connection.execute(query).scalar_one())


# ============================================================
# INSERT EVENT
# ============================================================

def insert_event(
    event_df,
    event_number
):

    event_code = generate_event_code(
        event_number
    )


    latitude, longitude = (
        calculate_event_center(
            event_df
        )
    )


    first_detected = (
        event_df["timestamp"].min()
    )


    last_detected = (
        event_df["timestamp"].max()
    )


    detection_count = len(
        event_df
    )


    persistence_status = (
        determine_persistence(
            event_df
        )
    )


    confidence = (
        calculate_confidence(
            event_df
        )
    )


    risk_score = (
        calculate_risk_score(
            event_df
        )
    )


    risk_level = (
        determine_risk_level(
            risk_score
        )
    )


    # IMPORTANT:
    #
    # This is NOT the final classification.
    #
    # We currently only know that
    # the event is a thermal anomaly.

    current_class = (
        "THERMAL_ANOMALY"
    )


    status = "ACTIVE"


    query = text(
        """
        INSERT INTO events

        (
            event_code,

            geometry,

            first_detected,

            last_detected,

            detection_count,

            persistence_status,

            current_class,

            confidence,

            risk_score,

            risk_level,

            status

        )

        VALUES

        (
            :event_code,

            ST_SetSRID(

                ST_MakePoint(
                    :longitude,
                    :latitude
                ),

                4326

            ),

            :first_detected,

            :last_detected,

            :detection_count,

            :persistence_status,

            :current_class,

            :confidence,

            :risk_score,

            :risk_level,

            :status
        )

        RETURNING id;
        """
    )


    with engine.begin() as connection:

        result = connection.execute(

            query,

            {
                "event_code":
                    event_code,

                "longitude":
                    longitude,

                "latitude":
                    latitude,

                "first_detected":
                    first_detected,

                "last_detected":
                    last_detected,

                "detection_count":
                    detection_count,

                "persistence_status":
                    persistence_status,

                "current_class":
                    current_class,

                "confidence":
                    confidence,

                "risk_score":
                    risk_score,

                "risk_level":
                    risk_level,

                "status":
                    status
            }

        )


        event_id = result.scalar_one()


    return event_id


# ============================================================
# LINK DETECTIONS TO EVENT
# ============================================================

def link_detections(
    event_df,
    event_id
):

    detection_ids = (
        event_df["id"]
        .astype(int)
        .tolist()
    )


    if not detection_ids:

        return


    query = text(
        """
        UPDATE thermal_anomalies

        SET event_id = :event_id

        WHERE id = ANY(
            CAST(:detection_ids AS INTEGER[])
        );
        """
    )


    with engine.begin() as connection:

        connection.execute(

            query,

            {
                "event_id":
                    event_id,

                "detection_ids":
                    detection_ids
            }

        )


# ============================================================
# EVENT CSV EXPORT
# ============================================================

def export_events_csv():

    query = text(
        """
        SELECT
            event_code AS event_id,
            ST_Y(geometry) AS latitude,
            ST_X(geometry) AS longitude,
            first_detected AS first_detection,
            last_detected AS last_detection,
            detection_count
        FROM events
        ORDER BY id;
        """
    )

    with engine.connect() as connection:

        events_df = pd.read_sql(
            query,
            connection
        )

    output_path = (
        os.path.dirname(__file__)
        + "/data/events/events.csv"
    )

    os.makedirs(
        os.path.dirname(output_path),
        exist_ok=True
    )

    events_df.to_csv(
        output_path,
        index=False
    )

    print(
        f"Events exported: {output_path}"
    )


# ============================================================
# PROCESS EVENTS
# ============================================================

def process_events(df):

    if df.empty:

        print(
            "No detections available."
        )

        return


    # --------------------------------------------------------
    # Build timestamp
    # --------------------------------------------------------

    df = build_timestamp(df)


    # Remove invalid timestamps.

    invalid_count = (
        df["timestamp"]
        .isna()
        .sum()
    )


    if invalid_count:

        print(
            f"Removing "
            f"{invalid_count} detections "
            f"with invalid timestamps."
        )


    df = df.dropna(
        subset=["timestamp"]
    )


    if df.empty:

        print(
            "No valid detections remain."
        )

        return


    # --------------------------------------------------------
    # Spatial clustering
    # --------------------------------------------------------

    print(
        "\nRunning spatial DBSCAN..."
    )


    df = spatial_clustering(
        df
    )


    spatial_count = (
        df["spatial_cluster"]
        .nunique()
    )


    print(
        f"Spatial clusters: "
        f"{spatial_count}"
    )


    # --------------------------------------------------------
    # Temporal grouping
    # --------------------------------------------------------

    print(
        "\nApplying temporal grouping..."
    )


    df = temporal_clustering(
        df
    )


    event_count = (
        df["event_cluster"]
        .nunique()
    )


    print(
        f"Final events: "
        f"{event_count}"
    )


    # --------------------------------------------------------
    # Create database events
    # --------------------------------------------------------

    print(
        "\nCreating database events..."
    )


    event_number = next_event_number()


    for cluster_id in sorted(

        df["event_cluster"].unique()

    ):

        event_df = (

            df[
                df["event_cluster"]
                == cluster_id
            ]

            .copy()

        )


        if event_df.empty:

            continue


        event_id = insert_event(

            event_df,

            event_number

        )


        link_detections(

            event_df,

            event_id

        )


        latitude, longitude = (
            calculate_event_center(
                event_df
            )
        )


        risk_score = (
            calculate_risk_score(
                event_df
            )
        )


        risk_level = (
            determine_risk_level(
                risk_score
            )
        )


        persistence = (
            determine_persistence(
                event_df
            )
        )


        print(
            "\n--------------------------------"
        )


        print(
            generate_event_code(
                event_number
            )
        )


        print(
            f"Event ID       : "
            f"{event_id}"
        )


        print(
            f"Detections     : "
            f"{len(event_df)}"
        )


        print(
            f"Center         : "
            f"{latitude:.5f}, "
            f"{longitude:.5f}"
        )


        print(
            f"Persistence    : "
            f"{persistence}"
        )


        print(
            f"Risk score     : "
            f"{risk_score}"
        )


        print(
            f"Risk level     : "
            f"{risk_level}"
        )


        event_number += 1


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n========================================"
    )

    print(
        "INDUSTRIAL FIRE EVENT ENGINE"
    )

    print(
        "========================================"
    )


    df = load_detections()


    print(
        f"\nThermal detections loaded: "
        f"{len(df)}"
    )

    pending_df = df[df["event_id"].isna()].copy()

    print(
        f"New detections to process: "
        f"{len(pending_df)}"
    )


    if pending_df.empty:

        print(
            "\nNo new thermal detections require processing."
        )

        export_events_csv()

        return


    process_events(
        pending_df
    )

    export_events_csv()


    print(
        "\n========================================"
    )

    print(
        "EVENT ENGINE COMPLETED"
    )

    print(
        "========================================"
    )


if __name__ == "__main__":

    main()