from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import ee
import numpy as np
import os

SERVICE_ACCOUNT_FILE = "gee_service_account.json"

credentials = ee.ServiceAccountCredentials(
    email=None,
    key_file=SERVICE_ACCOUNT_FILE
)
ee.Initialize(credentials)

app = FastAPI(title="TRINETRA Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "TRINETRA backend is running"}


@app.get("/api/gee-test")
def gee_test():
    image = ee.Image("USGS/SRTMGL1_003")
    info = image.getInfo()
    return {"connected": True, "dataset_id": info["id"]}


@app.get("/api/river-path")
def get_river_path():
    if not os.path.exists("full_river_polyline.npy"):
        return {"error": "full_river_polyline.npy not found. Run full_channel.py first."}

    polyline = np.load("full_river_polyline.npy")
    points = [
        {"lat": float(p[0]), "lon": float(p[1]), "elevation": float(p[2])}
        for p in polyline
    ]
    return {"count": len(points), "points": points}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
