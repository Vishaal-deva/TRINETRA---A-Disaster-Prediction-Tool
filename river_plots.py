import numpy as np

def segment_into_plots(polyline, num_plots=412):
    """
    Splits the ordered source->sink polyline into num_plots segments
    of roughly equal point-count. Each plot links to the next at a
    shared boundary coordinate (the last point of one = first point
    of the next), matching the sketch's "linked adjacent plots" idea.
    """
    n = len(polyline)
    plots = []
    step = n / num_plots

    for i in range(num_plots):
        start_idx = int(i * step)
        end_idx = int((i + 1) * step) if i < num_plots - 1 else n - 1
        segment = polyline[start_idx:end_idx + 1]
        plots.append(segment)

    return plots


if __name__ == "__main__":
    polyline = np.load("full_river_polyline.npy")
    plots = segment_into_plots(polyline, num_plots=412)

    print(f"Full river: {len(polyline)} points, split into {len(plots)} plots\n")

    for i, plot in enumerate(plots):
        start_lat, start_lon, start_elev = plot[0]
        end_lat, end_lon, end_elev = plot[-1]
        label = "SOURCE" if i == 0 else f"Plot {i}"
        print(f"{label}: {len(plot)} points")
        print(f"  Entry link point: ({start_lat:.5f}, {start_lon:.5f}), elev={start_elev:.1f}m")
        print(f"  Exit  link point: ({end_lat:.5f}, {end_lon:.5f}), elev={end_elev:.1f}m")
        if i == len(plots) - 1:
            print(f"  (This exit point = SINK)")
        print()

    np.save("river_plots.npy", np.array(plots, dtype=object), allow_pickle=True)
    print(f"Saved {len(plots)} linked plots to river_plots.npy")
