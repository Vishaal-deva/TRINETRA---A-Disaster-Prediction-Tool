import numpy as np
from dem_loader import load_dem
from flow_routing import fill_depressions, resolve_flats

elevation, transform, resolution, bounds = load_dem()
filled = fill_depressions(elevation)
filled = resolve_flats(filled)

r, c = 200, 195
print(f"Cell ({r},{c}) elevation: {filled[r, c]:.6f}")
print("\nNeighbor elevations:")
for dr in [-1, 0, 1]:
    row_vals = []
    for dc in [-1, 0, 1]:
        nr, nc = r + dr, c + dc
        row_vals.append(f"{filled[nr, nc]:.6f}")
    print("  ", row_vals)

print(f"\nDifference from center for each neighbor (positive = neighbor is LOWER = downhill):")
for dr in [-1, 0, 1]:
    for dc in [-1, 0, 1]:
        if dr == 0 and dc == 0:
            continue
        nr, nc = r + dr, c + dc
        diff = filled[r, c] - filled[nr, nc]
        print(f"  ({dr},{dc}): diff={diff:.6f}")
