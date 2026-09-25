import numpy as np
from dem_loader import load_dem


def find_steepest_descent_path(elevation, start_row, start_col, max_steps=500):
    """
    Traces a single path of water flow from (start_row, start_col),
    always moving to the lowest-elevation neighboring cell.
    Stops when no neighbor is lower (a local sink) or max_steps reached.

    Returns: list of (row, col, elevation) tuples along the path.
    """
    rows, cols = elevation.shape
    path = []

    r, c = start_row, start_col

    for _ in range(max_steps):
        current_elev = elevation[r, c]
        if np.isnan(current_elev):
            break

        path.append((r, c, float(current_elev)))

        # Check all 8 neighbors
        best_r, best_c = r, c
        best_elev = current_elev

        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    neighbor_elev = elevation[nr, nc]
                    if not np.isnan(neighbor_elev) and neighbor_elev < best_elev:
                        best_elev = neighbor_elev
                        best_r, best_c = nr, nc

        # No lower neighbor found — this is a local sink, water pools here
        if (best_r, best_c) == (r, c):
            break

        r, c = best_r, best_c

    return path


if __name__ == "__main__":
    elevation, transform, resolution, bounds = load_dem()

    # Start near the highest point in the tile — a rough stand-in
    # for "near the glacier/avalanche origin" until we pick a real breach point
    start_r, start_c = np.unravel_index(np.nanargmax(elevation), elevation.shape)
    print(f"Starting at pixel ({start_r}, {start_c}), elevation {elevation[start_r, start_c]:.1f}m")

    path = find_steepest_descent_path(elevation, start_r, start_c)

    print(f"\nPath length: {len(path)} steps")
    print(f"Start elevation: {path[0][2]:.1f}m")
    print(f"End elevation: {path[-1][2]:.1f}m")
    print(f"Total elevation drop: {path[0][2] - path[-1][2]:.1f}m")