import numpy as np
from scipy.interpolate import splprep, splev


def smooth_polyline(polyline, points_per_segment=10):
    lat = polyline[:, 0]
    lon = polyline[:, 1]
    elev = polyline[:, 2]

    tck, u = splprep([lat, lon, elev], s=0)
    n_fine = len(polyline) * points_per_segment
    u_fine = np.linspace(0, 1, n_fine)
    lat_s, lon_s, elev_s = splev(u_fine, tck)

    return np.column_stack([lat_s, lon_s, elev_s])


if __name__ == "__main__":
    polyline = np.load("full_river_polyline.npy")
    print(f"Loaded {len(polyline)} real points from full_river_polyline.npy")

    smoothed = smooth_polyline(polyline, points_per_segment=10)
    print(f"Produced {len(smoothed)} interpolated points for rendering")

    orig_min_elev = polyline[:, 2].min()
    orig_max_elev = polyline[:, 2].max()
    smooth_min_elev = smoothed[:, 2].min()
    smooth_max_elev = smoothed[:, 2].max()
    print(f"Original elevation range: {orig_min_elev:.1f}m to {orig_max_elev:.1f}m")
    print(f"Smoothed elevation range: {smooth_min_elev:.1f}m to {smooth_max_elev:.1f}m")

    np.save("full_river_polyline_smooth.npy", smoothed)
    print("Saved full_river_polyline_smooth.npy")
