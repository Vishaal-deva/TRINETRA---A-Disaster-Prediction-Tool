from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import ee
import numpy as np
import os
import json

key_json = os.environ["GEE_KEY_JSON"]
sa_email = json.loads(key_json)["client_email"]
credentials = ee.ServiceAccountCredentials(sa_email, key_data=key_json)
ee.Initialize(credentials, project="neon-flare-473204-u8")

app = FastAPI(title="TRINETRA Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://trinetra-frontend.onrender.com",
        "http://localhost:5173",
        "http://localhost:5174",
    ],
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
