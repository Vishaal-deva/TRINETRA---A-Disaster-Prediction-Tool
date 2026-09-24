import numpy as np
from scipy import ndimage
from dem_loader import load_dem


def fill_depressions(elevation):
    nan_mask = np.isnan(elevation)
    working = np.where(nan_mask, np.nanmax(elevation) + 1, elevation)

    marker = np.full_like(working, np.max(working))
    marker[0, :] = working[0, :]
    marker[-1, :] = working[-1, :]
    marker[:, 0] = working[:, 0]
    marker[:, -1] = working[:, -1]

    filled = marker.copy()
    prev = None
    while prev is None or not np.array_equal(filled, prev):
        prev = filled
        eroded = ndimage.grey_erosion(filled, size=3)
        filled = np.maximum(eroded, working)

    filled[nan_mask] = np.nan
    return filled


def resolve_flats(filled_elevation, epsilon=1e-6):
    filled_elevation = filled_elevation.astype(np.float64)
    rows, cols = filled_elevation.shape
    tilt = np.arange(rows * cols, dtype=np.float64).reshape(rows, cols) * epsilon
    return filled_elevation - tilt


def compute_flow_direction(filled_elevation):
    rows, cols = filled_elevation.shape
    flow_to = np.full((rows, cols, 2), -1, dtype=int)

    neighbors = [(-1, -1, np.sqrt(2)), (-1, 0, 1), (-1, 1, np.sqrt(2)),
                 (0, -1, 1),                        (0, 1, 1),
                 (1, -1, np.sqrt(2)),  (1, 0, 1),  (1, 1, np.sqrt(2))]

    for r in range(rows):
        for c in range(cols):
            if np.isnan(filled_elevation[r, c]):
                continue
            best_slope = 0
            best_target = None
            for dr, dc, dist in neighbors:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    nelev = filled_elevation[nr, nc]
                    if not np.isnan(nelev):
                        drop = filled_elevation[r, c] - nelev
                        slope = drop / dist
                        if slope > best_slope:
                            best_slope = slope
                            best_target = (nr, nc)
            if best_target:
                flow_to[r, c] = best_target

    acc = np.ones((rows, cols), dtype=int)
    order = np.dstack(np.unravel_index(
        np.argsort(-np.nan_to_num(filled_elevation, nan=-np.inf), axis=None),
        filled_elevation.shape))[0]

    for r, c in order:
        target = flow_to[r, c]
        if target[0] != -1:
            acc[target[0], target[1]] += acc[r, c]

    return flow_to, acc


if __name__ == "__main__":
    elevation, transform, resolution, bounds = load_dem()

    print("Filling depressions...")
    filled = fill_depressions(elevation)

    print("Resolving flats...")
    filled = resolve_flats(filled)

    print("Computing flow direction and accumulation...")
    flow_to, acc = compute_flow_direction(filled)

    print("\nFlow accumulation stats:")
    print("  Min:", acc.min())
    print("  Max:", acc.max())
    print("  Mean:", acc.mean())

    max_idx = np.unravel_index(np.argmax(acc), acc.shape)
    print(f"\nHighest-accumulation cell at (row={max_idx[0]}, col={max_idx[1]})")
    print(f"Accumulation value there: {acc[max_idx]}")
    print(f"Elevation there: {filled[max_idx]:.1f}m")
