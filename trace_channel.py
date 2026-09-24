import numpy as np
from dem_loader import load_dem
from flow_routing import fill_depressions, resolve_flats, compute_flow_direction


def find_nearest_lower(filled_elevation, r, c, max_radius=15):
    rows, cols = filled_elevation.shape
    current = filled_elevation[r, c]
    for radius in range(1, max_radius + 1):
        best = None
        best_elev = current
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                if abs(dr) != radius and abs(dc) != radius:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    e = filled_elevation[nr, nc]
                    if not np.isnan(e) and e < best_elev:
                        best_elev = e
                        best = (nr, nc)
        if best:
            return best
    return None


def trace_downstream(flow_to, filled_elevation, start_row, start_col, max_steps=1000):
    path = []
    r, c = start_row, start_col
    rows, cols = filled_elevation.shape

    for _ in range(max_steps):
        path.append((r, c, float(filled_elevation[r, c])))
        target = flow_to[r, c]

        if target[0] == -1:
            jump = find_nearest_lower(filled_elevation, r, c)
            if jump is None:
                break
            r, c = jump
        else:
            r, c = target[0], target[1]

        if not (0 <= r < rows and 0 <= c < cols):
            break

    return path


if __name__ == "__main__":
    elevation, transform, resolution, bounds = load_dem()
    print("Filling depressions...")
    filled = fill_depressions(elevation)
    print("Resolving flats...")
    filled = resolve_flats(filled)
    print("Computing flow direction and accumulation...")
    flow_to, acc = compute_flow_direction(filled)

    start_row, start_col = 200, 195
    path = trace_downstream(flow_to, filled, start_row, start_col)

    print(f"\nTraced path: {len(path)} steps")
    print(f"Start: row={path[0][0]}, col={path[0][1]}, elevation={path[0][2]:.1f}m")
    print(f"End:   row={path[-1][0]}, col={path[-1][1]}, elevation={path[-1][2]:.1f}m")
    print(f"Total drop: {path[0][2] - path[-1][2]:.1f}m over {len(path)} steps")

    print("\nSample points along the path:")
    for i in range(0, len(path), max(1, len(path) // 15)):
        r, c, e = path[i]
        lon = transform.c + c * transform.a
        lat = transform.f + r * transform.e
        print(f"  step {i}: ({lat:.5f}N, {lon:.5f}E), elevation={e:.1f}m")

    end_r, end_c, end_e = path[-1]
    end_lon = transform.c + end_c * transform.a
    end_lat = transform.f + end_r * transform.e
    print(f"\nEndpoint coordinate to check on map: {end_lat:.5f}, {end_lon:.5f}")
