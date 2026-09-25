import numpy as np
from math import radians, sin, cos, sqrt, atan2
from dem_loader import load_dem
from flow_routing import fill_depressions, compute_flow_direction


def build_reverse_flow_map(flow_to):
    rows, cols = flow_to.shape[:2]
    reverse_map = {}
    for r in range(rows):
        for c in range(cols):
            t = flow_to[r, c]
            if t[0] != -1:
                key = (t[0], t[1])
                reverse_map.setdefault(key, []).append((r, c))
    return reverse_map


def trace_main_channel_upstream(acc, reverse_map, outlet, channel_threshold=500, max_steps=2000):
    path = [outlet]
    current = outlet

    for _ in range(max_steps):
        incoming = reverse_map.get(current, [])
        if not incoming:
            break
        best = max(incoming, key=lambda rc: acc[rc[0], rc[1]])
        if acc[best[0], best[1]] < channel_threshold:
            break
        path.append(best)
        current = best

    path.reverse()
    return path


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

    print("Computing flow direction and accumulation...")
    flow_to, acc = compute_flow_direction(filled)

    print("Building reverse flow map...")
    reverse_map = build_reverse_flow_map(flow_to)

    outlet = tuple(np.unravel_index(np.argmax(acc), acc.shape))
    print(f"\nOutlet (max accumulation point): {outlet}, acc={acc[outlet]}")

    channel_points = trace_main_channel_upstream(acc, reverse_map, outlet, channel_threshold=500)

    print(f"\nMain channel: {len(channel_points)} points, source -> sink")
    print(f"Source: {channel_points[0]}, elevation={filled[channel_points[0]]:.1f}m")
    print(f"Sink:   {channel_points[-1]}, elevation={filled[channel_points[-1]]:.1f}m")

    river_polyline = []
    for r, c in channel_points:
        lon = transform.c + c * transform.a
        lat = transform.f + r * transform.e
        river_polyline.append((lat, lon, float(filled[r, c])))

    total_km = 0.0
    for i in range(len(river_polyline) - 1):
        lat1, lon1, _ = river_polyline[i]
        lat2, lon2, _ = river_polyline[i + 1]
        total_km += haversine_km(lat1, lon1, lat2, lon2)

    print(f"\nTraced segment length: {total_km:.3f} km over {len(river_polyline)} points")
    print("This is only the upstream portion currently traced, not full source to sink")

    np.save("river_polyline.npy", np.array(river_polyline))
    print(f"Saved {len(river_polyline)} points to river_polyline.npy")
