import rasterio
import numpy as np

with rasterio.open("rishiganga_dem.tif") as src:
    print("Driver:", src.driver)
    print("CRS:", src.crs)
    print("Width x Height:", src.width, "x", src.height)
    print("Bounds:", src.bounds)

    elevation = src.read(1)
    valid = elevation[elevation != src.nodata] if src.nodata is not None else elevation

    print("\nElevation stats (meters):")
    print("  Min:", np.min(valid))
    print("  Max:", np.max(valid))
    print("  Mean:", np.mean(valid))
    print("  Nodata value:", src.nodata)