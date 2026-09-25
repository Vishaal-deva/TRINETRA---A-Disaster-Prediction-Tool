import rasterio
import numpy as np

def load_dem(filepath="rishiganga_dem.tif"):
    """
    Loads a GeoTIFF DEM and returns:
      - elevation: 2D numpy array (meters), nodata replaced with np.nan
      - transform: rasterio Affine transform (maps pixel coords -> real lat/lon)
      - resolution: (x_res, y_res) in degrees per pixel
      - bounds: (west, south, east, north)
    """
    with rasterio.open(filepath) as src:
        elevation = src.read(1).astype(np.float32)

        if src.nodata is not None:
            elevation[elevation == src.nodata] = np.nan

        transform = src.transform
        resolution = (transform.a, -transform.e)  # x_res, y_res (positive)
        bounds = src.bounds

    return elevation, transform, resolution, bounds


if __name__ == "__main__":
    elev, transform, res, bounds = load_dem()
    print("Shape:", elev.shape)
    print("Resolution (deg/pixel):", res)
    print("Bounds:", bounds)
    print("Min/Max/Mean (ignoring NaN):",
          np.nanmin(elev), np.nanmax(elev), np.nanmean(elev))