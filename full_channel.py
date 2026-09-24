import numpy as np
from dem_loader import load_dem
from flow_routing import fill_depressions, resolve_flats, compute_flow_direction
from channel_path import build_reverse_flow_map, trace_main_channel_upstream
from trace_channel import trace_downstream
from math import radians, sin, cos, sqrt, atan2


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


if __name__ == "__main__":
    elevation, transform, resolution, bounds = load_dem()
    print("Filling depressions...")
    filled = fill_depressions(elevation)
    print("Resolving flats...")
    filled = resolve_flats(filled)
    print("Computing flow direction and accumulation...")
    flow_to, acc = compute_flow_direction(filled)

    outlet = tuple(np.unravel_index(np.argmax(acc), acc.shape))
    reverse_map = build_reverse_flow_map(flow_to)

    upstream = trace_main_channel_upstream(acc, reverse_map, outlet, channel_threshold=500)
    downstream_path = trace_downstream(flow_to, filled, outlet[0], outlet[1])
    downstream = [(r, c) for r, c, e in downstream_path]

    full_path = upstream[:-1] + downstream

    print(f"\nFull path: {len(full_path)} points (source -> sink)")

    polyline = []
    for r, c in full_path:
        lon = transform.c + c * transform.a
        lat = transform.f + r * transform.e
        polyline.append((lat, lon, float(filled[r, c])))

    total_km = 0.0
    for i in range(len(polyline) - 1):
        lat1, lon1, _ = polyline[i]
        lat2, lon2, _ = polyline[i + 1]
        total_km += haversine_km(lat1, lon1, lat2, lon2)

    print(f"Source: {polyline[0][:2]}, elevation={polyline[0][2]:.1f}m")
    print(f"Sink:   {polyline[-1][:2]}, elevation={polyline[-1][2]:.1f}m")
    print(f"Total elevation drop: {polyline[0][2] - polyline[-1][2]:.1f}m")
    print(f"\nTOTAL RIVER LENGTH THROUGH TILE: {total_km:.3f} km")

    np.save("full_river_polyline.npy", np.array(polyline))
    print(f"Saved {len(polyline)} points to full_river_polyline.npy")
