import ee

ee.Initialize(project="neon-flare-473204-u8")

# Simple test: get info about a well-known public dataset
image = ee.Image("USGS/SRTMGL1_003")
info = image.getInfo()
print("Connected successfully!")
print("Dataset:", info["id"])

