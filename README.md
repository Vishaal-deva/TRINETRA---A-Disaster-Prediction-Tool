# TRINETRA ~ Disaster Prediction Tool

Live demo: https://trinetra-lovat.vercel.app

### Current Status : web link available .

## What it does

TRINETRA predicts dam-break and flash-flood events instead of only simulating them afterwards. It watches surrounding calamity signals (seismic, landslide, rainfall) together with abnormal water-pressure differential, and uses them as detection triggers for a downstream inundation forecast.

The working prototype is scoped to one river, the Rishiganga, using a real ~8x9 km terrain tile.



| Component | Status |
|---|---|
| Real DEM (SRTM GL1, ~30 m) for Rishiganga | Done |
| Flow routing (depression fill + D8) and channel extraction | Done |
| Source-to-sink river polyline (206 points, ~8.85 km) | Done |
| FastAPI backend with Google Earth Engine access | Running locally |
| Cesium + Vite frontend rendering the real river polyline | Working |
| Hydrodynamic simulation core (SPH + Delft3D) | Planned |
| AI trigger classifier (breach probability) | Planned |
| Sentinel-1/2 and CHIRPS data pulls | Planned |
| Authority dashboard | Planned |

## Architecture

Open Data Layer -> GEE/API Integration -> Terrain & Flow Prep -> Simulation Core -> Risk & Trigger Fusion -> Inundation Forecast -> Historical Validation -> Decision Optimization -> Authority Dashboard

## Repository layout
## Tech stack

- Backend: Python, FastAPI, NumPy/SciPy, Google Earth Engine
- Frontend: CesiumJS, Vite
- Planned: DualSPHysics, Delft3D, PostGIS

## Run locally

### Backend
The backend authenticates to Google Earth Engine with a service account. Set the credentials as environment variables before starting (check backend/main.py for the exact variable names). Never commit the key file.

### Frontend
Open the local URL that Vite prints.

## Roadmap

1. Cesium World Terrain for 3D relief
2. Split the river into linked sequential reaches for simulation and visualization
3. Simulation core for flood spread
4. Trigger classifier on seismic, landslide, rainfall and pressure signals
5. Authority dashboard and deployment of backend and frontend

## Known limits

- The exact dam site coordinates are not yet anchored. The prototype currently uses the DEM-derived max flow-accumulation point (30.40458 N, 79.73403 E), which is upstream of the real dam.
- Only the Rishiganga is functional. Other rivers are not implemented.

## Team

Kshetra Labs
