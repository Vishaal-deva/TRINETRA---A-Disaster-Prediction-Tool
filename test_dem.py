import os
import requests

API_KEY = os.environ.get("OPENTOPOGRAPHY_API_KEY")
if not API_KEY:
    raise RuntimeError("OPENTOPOGRAPHY_API_KEY not set — did you export it?")

# Rishiganga bounding box (~8km x 9km)
params = {
    "demtype": "SRTMGL1",
    "south": 30.38, "north": 30.46,
    "west": 79.68, "east": 79.78,
    "outputFormat": "GTiff",
    "API_Key": API_KEY,
}

resp = requests.get("https://portal.opentopography.org/API/globaldem", params=params, timeout=60)
print("Status code:", resp.status_code)

if resp.status_code == 200:
    with open("rishiganga_dem.tif", "wb") as f:
        f.write(resp.content)
    print("Saved rishiganga_dem.tif —", len(resp.content), "bytes")
else:
    print("Error response:", resp.text)