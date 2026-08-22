# Industrial Thermal Intelligence - Web Dashboard

A modern, dark-mode geospatial dashboard built with **React**, **TypeScript**, **Tailwind CSS**, and **Leaflet** for real-time satellite thermal anomaly monitoring, classification, and industrial fire risk intelligence.

---

## Features

- 🛰️ **Interactive Satellite GIS Map**: Dark-themed geospatial map visualizing satellite hotspots with color-coded classification markers (Industrial Fire 🔴, Wildfire 🟧, Agricultural 🟨, Persistent Flare 🟣).
- 📊 **Real-Time KPI Summary Bar**: Top metric cards displaying total events, active industrial fires, flares, and high-risk alerts.
- 🔬 **Event Telemetry Inspector**: Detailed analytics drawer displaying Fire Radiative Power (FRP max/mean), proximity to industrial facilities (meters), land cover breakdown charts (industrial, forest, built-up), and AI persistence risk scores.
- 🔍 **Filter & Search Panel**: Instant filtering by Event ID, persistence status, and high-detection density.

---

## How to Run

### 1. Start the Backend API (FastAPI)

Ensure Python dependencies are installed and start the backend server:

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

The API will run at `http://localhost:8000`.

### 2. Start the Frontend Dashboard

Ensure Node.js is installed, then run:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.
