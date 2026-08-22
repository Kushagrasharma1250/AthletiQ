# Backend

The backend is a FastAPI service for the Industrial Fire Intelligence dashboard. It serves event summaries, persistent thermal sources, aggregate statistics, and detailed event telemetry from generated CSV data. Supporting modules ingest NASA FIRMS data, build event clusters, engineer features, run classification, and persist results in PostgreSQL/PostGIS.

## Requirements

- Python 3.10 or newer
- PostgreSQL with PostGIS, or Docker Desktop
- A NASA FIRMS map key for live ingestion

The repository currently does not include `backend/requirements.txt`. The backend imports FastAPI, Uvicorn, pandas, NumPy, python-dotenv, SQLAlchemy, scikit-learn, requests, and joblib. Install the dependencies in the active Python environment before running the service.

## Configuration

Create `backend/.env` for database-backed ingestion and event processing:

```env
DATABASE_URL=postgresql+psycopg2://fire_admin:131006@localhost:5432/fire_intelligence
NASA_FIRMS_MAP_KEY=your_nasa_firms_map_key
```

`main.py` reads the generated CSV files under `backend/data` and does not require a database connection to serve the dashboard endpoints. `event_engine.py`, `firm_ingestion.py`, and the database modules do require `DATABASE_URL`. Keep API keys and database credentials out of source control.

## Start PostgreSQL

The included Compose configuration starts PostGIS on port `5432`:

```powershell
docker compose up -d postgres
```

The database settings are defined in `docker-compose.yml`:

- Database: `fire_intelligence`
- User: `fire_admin`
- Port: `5432`

Initialize the database with the SQL scripts in `backend/database` as required by the current pipeline.

## Run the API

From the repository root, activate the project environment and start Uvicorn:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
uvicorn main:app --reload --port 8000
```

The API is available at `http://localhost:8000`. Interactive API documentation is available at `http://localhost:8000/docs`, with the OpenAPI schema at `http://localhost:8000/openapi.json`.

## API Endpoints

### `GET /`

Returns the service name and online status.

### `GET /health`

Returns:

```json
{"status": "healthy"}
```

### `GET /events`

Returns event map summaries from `backend/data/events/events.csv`:

```json
{
  "events": [
    {
      "event_id": "EVT_2026_001",
      "latitude": 29.9511,
      "longitude": -90.0715,
      "detection_count": 12
    }
  ]
}
```

If the CSV is missing, the endpoint returns an empty event list.

### `GET /events/persistent`

Returns rows marked `PERSISTENT` in `backend/data/features/event_features.csv`, including the persistence score and total count.

### `GET /statistics`

Returns aggregate totals derived from the processed training data and event features:

- `total_events`
- `industrial_fires`
- `wildfires`
- `agricultural_burning`
- `persistent_sources`
- `recurring_events`
- `high_risk_events`

### `GET /events/{event_id}`

Returns thermal, spatial, land-cover, temporal, and persistence details for one event. The endpoint returns HTTP 404 when the feature file or requested event is unavailable.

## Data Flow

1. `firm_ingestion.py` fetches and cleans VIIRS thermal anomalies from NASA FIRMS.
2. `backend/database` contains the database connection and schema scripts for PostgreSQL/PostGIS.
3. `event_engine.py` loads thermal detections and groups nearby detections into events using spatial and temporal rules.
4. `feature_engineering` builds thermal, spatial, land-cover, and temporal features.
5. `ml/training/train_model.py` trains the industrial fire classifier; the trained model is stored under `ml/models`.
6. `ml/inference/predict.py` provides model prediction logic.
7. `persistence` and `pipeline` contain persistence detection and processing workflow code.
8. The API reads the generated CSV outputs and exposes them to the frontend.

## Generated Data Files

The API expects these files when they are available:

- `backend/data/events/events.csv`: event map summaries
- `backend/data/features/event_features.csv`: event-level feature and persistence data
- `backend/data/processed/training_with_recurrence.csv`: classification and aggregate statistics data
- `backend/data/firms/`: downloaded and cleaned FIRMS data

## Frontend Integration

The frontend defaults to `http://localhost:8000`. To use another API host, set `VITE_API_URL` in the frontend environment. CORS is currently enabled for `http://localhost:5173` and `http://127.0.0.1:5173`.

## Quick Checks

With the API running:

```powershell
Invoke-RestMethod http://localhost:8000/health
Invoke-RestMethod http://localhost:8000/events
Invoke-RestMethod http://localhost:8000/statistics
```
