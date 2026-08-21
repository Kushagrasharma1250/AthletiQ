import os
from io import StringIO
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv



# CONFIGURATION


load_dotenv()

MAP_KEY = os.getenv("NASA_FIRMS_MAP_KEY")

BASE_URL = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"

DATA_DIR = Path(__file__).parent / "data" / "firms"

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)



# VALIDATE API KEY


if not MAP_KEY:
    raise RuntimeError(
        "NASA_FIRMS_MAP_KEY was not found in .env"
    )



# FETCH DATA FROM NASA FIRMS


def fetch_viirs_data(
    west: float,
    south: float,
    east: float,
    north: float,
    days: int = 5,
    source: str = "VIIRS_NOAA21_NRT",
) -> pd.DataFrame:

    """
    Fetch VIIRS thermal anomaly data from NASA FIRMS.

    Parameters
    ----------
    west : float
        Western longitude.

    south : float
        Southern latitude.

    east : float
        Eastern longitude.

    north : float
        Northern latitude.

    days : int
        Number of days to retrieve.
        FIRMS Area API supports up to 5 days.

    source : str
        FIRMS data source.

    Returns
    -------
    pandas.DataFrame
    """

    if days < 1 or days > 5:
        raise ValueError(
            "days must be between 1 and 5."
        )

    area = f"{west},{south},{east},{north}"

    url = (
        f"{BASE_URL}/"
        f"{MAP_KEY}/"
        f"{source}/"
        f"{area}/"
        f"{days}"
    )

    print("\n========================================")
    print("NASA FIRMS REQUEST")
    print("========================================")

    print(f"Source : {source}")
    print(f"Area   : {area}")
    print(f"Days   : {days}")

    try:

        response = requests.get(
            url,
            timeout=60
        )

        response.raise_for_status()

    except requests.exceptions.RequestException as error:

        print("\nFIRMS API request failed.")

        print(
            f"Error: {error}"
        )

        raise

    print(
        f"\nHTTP Status: {response.status_code}"
    )


    # Check response


    if not response.text.strip():

        print(
            "\nNASA FIRMS returned an empty response."
        )

        return pd.DataFrame()


    # Convert CSV → DataFrame


    df = pd.read_csv(
        StringIO(response.text)
    )

    return df



# CLEAN VIIRS DATA


def clean_viirs_data(
    df: pd.DataFrame
) -> pd.DataFrame:

    """
    Clean and validate FIRMS VIIRS data.
    """

    if df.empty:

        return df

    print("\n========================================")
    print("DATA CLEANING")
    print("========================================")


    # Required columns


    required_columns = [
        "latitude",
        "longitude",
        "bright_ti4",
        "scan",
        "track",
        "acq_date",
        "acq_time",
        "satellite",
        "instrument",
        "confidence",
        "version",
        "bright_ti5",
        "frp",
        "daynight",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            "Missing FIRMS columns: "
            + ", ".join(missing_columns)
        )


    # Numeric columns


    numeric_columns = [
        "latitude",
        "longitude",
        "bright_ti4",
        "scan",
        "track",
        "bright_ti5",
        "frp",
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )


    # Remove invalid coordinates


    before = len(df)

    df = df.dropna(
        subset=[
            "latitude",
            "longitude"
        ]
    )

    df = df[
        (df["latitude"] >= -90)
        &
        (df["latitude"] <= 90)
        &
        (df["longitude"] >= -180)
        &
        (df["longitude"] <= 180)
    ]

    removed = before - len(df)

    print(
        f"Invalid records removed: {removed}"
    )

    return df



# CREATE INTERNAL THERMAL ANOMALY SCHEMA


def transform_to_thermal_anomalies(
    df: pd.DataFrame
) -> pd.DataFrame:

    """
    Convert NASA FIRMS schema into our
    application's internal schema.
    """

    if df.empty:

        return df

    result = pd.DataFrame()


    # Location


    result["latitude"] = df["latitude"]

    result["longitude"] = df["longitude"]


    # Acquisition information


    result["acquisition_date"] = pd.to_datetime(
        df["acq_date"],
        errors="coerce"
    )

    result["acquisition_time"] = (
        df["acq_time"]
        .astype(str)
        .str.zfill(4)
    )


    # Thermal measurements


    result["brightness_temperature"] = (
        df["bright_ti4"]
    )

    result["background_temperature"] = (
        df["bright_ti5"]
    )


    # Fire Radiative Power


    result["frp"] = df["frp"]


    # Detection confidence


    result["confidence"] = (
        df["confidence"]
        .astype(str)
    )


    # Satellite information


    result["satellite"] = (
        df["satellite"]
    )

    result["instrument"] = (
        df["instrument"]
    )

    result["daynight"] = (
        df["daynight"]
    )


    # Source


    result["source"] = "NASA_FIRMS"

    result["source_dataset"] = (
        "VIIRS_NOAA21_NRT"
    )


    # Initial classification


    result["anomaly_type"] = (
        "THERMAL_ANOMALY"
    )


    # Future intelligence fields


    result["industrial_proximity"] = None

    result["distance_to_industry_m"] = None

    result["risk_score"] = None

    result["classification"] = None

    return result



# SAVE RAW DATA


def save_raw_data(
    df: pd.DataFrame
):

    if df.empty:

        return None

    output_path = (
        DATA_DIR
        / "viirs_raw.csv"
    )

    df.to_csv(
        output_path,
        index=False
    )

    print(
        f"\nRaw data saved to:"
    )

    print(output_path)

    return output_path



# SAVE NORMALIZED DATA


def save_normalized_data(
    df: pd.DataFrame
):

    if df.empty:

        return None

    output_path = (
        DATA_DIR
        / "thermal_anomalies.csv"
    )

    df.to_csv(
        output_path,
        index=False
    )

    print(
        f"\nNormalized data saved to:"
    )

    print(output_path)

    return output_path



# DISPLAY SUMMARY


def display_summary(
    df: pd.DataFrame
):

    if df.empty:

        print(
            "\nNo thermal anomalies found."
        )

        return

    print("\n========================================")
    print("INGESTION SUMMARY")
    print("========================================")

    print(
        f"Total detections : {len(df)}"
    )

    print(
        f"Satellites       : "
        f"{df['satellite'].unique().tolist()}"
    )

    print(
        f"Date range       : "
        f"{df['acquisition_date'].min().date()} "
        f"to "
        f"{df['acquisition_date'].max().date()}"
    )

    print(
        f"Average FRP      : "
        f"{df['frp'].mean():.2f} MW"
    )

    print(
        f"Maximum FRP      : "
        f"{df['frp'].max():.2f} MW"
    )

    print(
        f"Average brightness: "
        f"{df['brightness_temperature'].mean():.2f} K"
    )

    print("\nFirst 5 detections:")

    print(
        df[
            [
                "latitude",
                "longitude",
                "acquisition_date",
                "frp",
                "brightness_temperature",
                "confidence",
                "satellite",
            ]
        ].head()
    )



# MAIN PIPELINE


def main():

    print("\n")
    print("========================================")
    print("INDUSTRIAL FIRE INTELLIGENCE SYSTEM")
    print("NASA FIRMS INGESTION")
    print("========================================")


    # TEST REGION
    #
    # West   = 76
    # South  = 27
    # East   = 79
    # North  = 30
    #
    # This covers a large part of North India.


    west = 76.0
    south = 27.0
    east = 79.0
    north = 30.0


    # Retrieve last 5 days


    raw_df = fetch_viirs_data(
        west=west,
        south=south,
        east=east,
        north=north,
        days=5,
        source="VIIRS_NOAA21_NRT",
    )

    print(
        f"\nRaw detections received: "
        f"{len(raw_df)}"
    )


    # Handle empty response


    if raw_df.empty:

        print(
            "\nNo thermal anomalies found."
        )

        return


    # Save NASA's original data


    save_raw_data(
        raw_df
    )


    # Clean data


    cleaned_df = clean_viirs_data(
        raw_df
    )

    print(
        f"Valid detections: "
        f"{len(cleaned_df)}"
    )

    if cleaned_df.empty:

        print(
            "\nNo valid detections after cleaning."
        )

        return


    # Transform to application schema


    thermal_df = (
        transform_to_thermal_anomalies(
            cleaned_df
        )
    )


    # Save normalized data


    save_normalized_data(
        thermal_df
    )


    # Display summary


    display_summary(
        thermal_df
    )

    print("\n========================================")
    print("INGESTION COMPLETED SUCCESSFULLY")
    print("========================================")


if __name__ == "__main__":

    main()