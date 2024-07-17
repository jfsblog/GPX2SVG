# pip install gpxpy svgwrite geopy

import tkinter as tk
from tkinter import filedialog, messagebox
import gpxpy
from geopy.distance import geodesic
import svgwrite


def parse_gpx(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as gpx_file:
            gpx = gpxpy.parse(gpx_file)

        points = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    points.append((point.longitude, point.latitude))
        return points
    except Exception as e:
        messagebox.showerror("Error", f"Failed to parse GPX file: {e}")
        return None


def calculate_distances(points):
    distances = []
    for i in range(1, len(points)):
        start = points[i - 1]
        end = points[i]
        distance = geodesic((start[1], start[0]), (end[1], end[0])).meters
        distances.append(distance)
    return distances


def create_svg(points, output_file, meters_per_cm, scale_factor=0.05, stroke_width=6):
    try:
        # Calculate total distances
        total_distance_x = sum([geodesic((points[i][1], points[i][0]), (points[i + 1][1], points[i + 1][0])).meters
                                for i in range(len(points) - 1)])
        total_distance_y = total_distance_x  # Assuming equal scaling for simplicity

        # Convert distances to cm and apply scale factor
        width_cm = (total_distance_x / meters_per_cm) * scale_factor
        height_cm = (total_distance_y / meters_per_cm) * scale_factor

        # Convert cm to pixels (assuming 96 DPI)
        width_px = width_cm * 96 / 2.54
        height_px = height_cm * 96 / 2.54

        dwg = svgwrite.Drawing(size=(width_px, height_px), debug=True)

        min_lon = min(point[0] for point in points)
        max_lon = max(point[0] for point in points)
        min_lat = min(point[1] for point in points)
        max_lat = max(point[1] for point in points)

        def scale_x(lon):
            return (lon - min_lon) / (max_lon - min_lon) * width_px

        def scale_y(lat):
            return height_px - (lat - min_lat) / (max_lat - min_lat) * height_px

        scaled_points = [(scale_x(lon), scale_y(lat)) for lon, lat in points]

        path = dwg.path(d='M {} {}'.format(scaled_points[0][0], scaled_points[0][1]),
                        stroke=svgwrite.rgb(10, 10, 16, '%'),
                        stroke_width=stroke_width,  # Set stroke width here
                        fill='none')

        for point in scaled_points[1:]:
            path.push('L {} {}'.format(point[0], point[1]))

        dwg.add(path)
        dwg.saveas(output_file)
        messagebox.showinfo("Success", f"SVG file saved successfully: {output_file}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to create SVG: {e}")


def browse_gpx_file():
    file_path = filedialog.askopenfilename(filetypes=[("GPX files", "*.gpx")])
    if file_path:
        gpx_entry.delete(0, tk.END)
        gpx_entry.insert(0, file_path)


def browse_output_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".svg", filetypes=[("SVG files", "*.svg")])
    if file_path:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, file_path)


def convert_gpx_to_svg():
    gpx_file_path = gpx_entry.get().strip()
    svg_output_path = output_entry.get().strip()
    meters_per_cm = float(meters_per_cm_entry.get().strip())
    scale_factor = float(scale_factor_entry.get().strip())

    if not gpx_file_path or not svg_output_path:
        messagebox.showerror("Error", "Please specify both GPX file and output SVG file paths.")
        return

    points = parse_gpx(gpx_file_path)
    if points:
        create_svg(points, svg_output_path, meters_per_cm, scale_factor)


# GUI setup
root = tk.Tk()
root.title("GPX to SVG Converter")

# Frame
frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

# GPX file entry and browse button
tk.Label(frame, text="GPX File:").grid(row=0, column=0, sticky=tk.E)
gpx_entry = tk.Entry(frame, width=50)
gpx_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Button(frame, text="Browse", command=browse_gpx_file).grid(row=0, column=2, padx=5, pady=5)

# Output file entry and browse button
tk.Label(frame, text="Output SVG File:").grid(row=1, column=0, sticky=tk.E)
output_entry = tk.Entry(frame, width=50)
output_entry.grid(row=1, column=1, padx=5, pady=5)
tk.Button(frame, text="Browse", command=browse_output_file).grid(row=1, column=2, padx=5, pady=5)

# Meters per cm entry
tk.Label(frame, text="Meters per cm:").grid(row=2, column=0, sticky=tk.E)
meters_per_cm_entry = tk.Entry(frame, width=10)
meters_per_cm_entry.grid(row=2, column=1, padx=5, pady=5)
meters_per_cm_entry.insert(0, "100")

# Scale factor entry
tk.Label(frame, text="Scale Factor:").grid(row=3, column=0, sticky=tk.E)
scale_factor_entry = tk.Entry(frame, width=10)
scale_factor_entry.grid(row=3, column=1, padx=5, pady=5)
scale_factor_entry.insert(0, "0.05")

# Convert button
tk.Button(frame, text="Convert", command=convert_gpx_to_svg).grid(row=4, columnspan=3, pady=10)

root.mainloop()