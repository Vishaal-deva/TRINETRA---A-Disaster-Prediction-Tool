import numpy as np
from dem_loader import load_dem
from flow_routing import fill_depressions, compute_flow_direction


def extract_channel(acc, threshold=50):
    """
    Marks cells as 'channel' if their flow accumulation exceeds
    the threshold — i.e. enough upstream area drains through them
    that they're very likely part of the real river network, not
    just a random hillside cell.

    Returns a boolean mask, same shape as acc.
    """
    return acc >= threshold


def latlon_to_pixel(lat, lon, transform):
    """
    Converts real-world lat/lon into (row, col) pixel indices,
    using the DEM's affine transform (inverse of pixel->coord).
    """
    col = int((lon - transform.c) / transform.a)
    row = int((lat - transform.f) / transform.e)
    return row, col


def find_nearest_channel_cell(channel_mask, row, col, max_search=20):
    """
    Given an approximate (row, col) — e.g. a known dam/breach site —
    searches outward in a growing box for the nearest actual channel
    cell, since the exact coordinate rarely lands precisely on a
    channel pixel.
    """
    rows, cols = channel_mask.shape
    for radius in range(max_search):
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                r, c = row + dr, col + dc
                if 0 <= r < rows and 0 <= c < cols and channel_mask[r, c]:
                    return r, c
    return None


if __name__ == "__main__":
    elevation, transform, resolution, bounds = load_dem()

    print("Filling depressions and computing flow routing...")
    filled = fill_depressions(elevation)
    flow_to, acc = compute_flow_direction(filled)

    for t in [50, 100, 200, 500, 1000]:
        mask = extract_channel(acc, threshold=t)
        pct = 100 * mask.sum() / mask.size
        print(f"Threshold {t}: {mask.sum()} cells ({pct:.2f}%)")

    channel_mask = extract_channel(acc, threshold=500)
    print(f"\nUsing threshold=500: {channel_mask.sum()} channel cells")

    # Use the single highest-accumulation cell in the WHOLE tile as
    # the main channel anchor — this is the strongest direct
    # hydrological signal we have (most upstream area draining
    # through one point), and it sits well inside the tile, not
    # near an edge where accumulation would be artificially low
    max_idx = np.unravel_index(np.argmax(acc), acc.shape)
    r, c = max_idx

    edge_margin = 10
    rows, cols = acc.shape
    near_edge = (r < edge_margin or r > rows - edge_margin or
                 c < edge_margin or c > cols - edge_margin)

    print(f"\nMax-accumulation cell (main channel anchor):")
    print(f"  Pixel: row={r}, col={c}")
    print(f"  Elevation: {filled[r, c]:.1f}m")
    print(f"  Flow accumulation: {acc[r, c]}")
    print(f"  Near tile edge (unreliable if True): {near_edge}")

    lon = transform.c + c * transform.a
    lat = transform.f + r * transform.e
    print(f"  Real-world coordinate: {lat:.5f}N, {lon:.5f}E")
    print(f"\n  --> Paste into Google Maps as: {lat:.5f}, {lon:.5f}")