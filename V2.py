# pip install gpxpy svgwrite geopy

import sys
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QLineEdit, QFileDialog, QMessageBox, QVBoxLayout, QHBoxLayout
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
        QMessageBox.critical(None, "錯誤", f"無法解析GPX文件：{e}")
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
        total_distance_x = sum([geodesic((points[i][1], points[i][0]), (points[i + 1][1], points[i + 1][0])).meters
                                for i in range(len(points) - 1)])
        total_distance_y = total_distance_x  # Assuming equal scaling for simplicity

        width_cm = (total_distance_x / meters_per_cm) * scale_factor
        height_cm = (total_distance_y / meters_per_cm) * scale_factor

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
                        stroke_width=stroke_width, 
                        fill='none')

        for point in scaled_points[1:]:
            path.push('L {} {}'.format(point[0], point[1]))

        dwg.add(path)
        dwg.saveas(output_file)
        QMessageBox.information(None, "成功", f"SVG文件已成功保存：{output_file}")
    except Exception as e:
        QMessageBox.critical(None, "錯誤", f"無法生成SVG文件：{e}")


def browse_gpx_file():
    file_path, _ = QFileDialog.getOpenFileName(None, "選擇GPX文件", "", "GPX文件 (*.gpx)")
    if file_path:
        gpx_entry.setText(file_path)


def browse_output_file():
    file_path, _ = QFileDialog.getSaveFileName(None, "保存SVG文件", "", "SVG文件 (*.svg)")
    if file_path:
        output_entry.setText(file_path)


def convert_gpx_to_svg():
    gpx_file_path = gpx_entry.text().strip()
    svg_output_path = output_entry.text().strip()
    meters_per_cm = float(meters_per_cm_entry.text().strip())
    scale_factor = float(scale_factor_entry.text().strip())

    if not gpx_file_path or not svg_output_path:
        QMessageBox.critical(None, "錯誤", "請指定GPX和SVG文件路徑。")
        return

    points = parse_gpx(gpx_file_path)
    if points:
        create_svg(points, svg_output_path, meters_per_cm, scale_factor)


# GUI setup
app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("GPX 轉換為 SVG")

layout = QVBoxLayout()

# GPX file entry and browse button
gpx_layout = QHBoxLayout()
gpx_label = QLabel("GPX文件：")
gpx_entry = QLineEdit()
gpx_button = QPushButton("瀏覽")
gpx_button.clicked.connect(browse_gpx_file)
gpx_layout.addWidget(gpx_label)
gpx_layout.addWidget(gpx_entry)
gpx_layout.addWidget(gpx_button)
layout.addLayout(gpx_layout)

# Output file entry and browse button
output_layout = QHBoxLayout()
output_label = QLabel("SVG文件：")
output_entry = QLineEdit()
output_button = QPushButton("瀏覽")
output_button.clicked.connect(browse_output_file)
output_layout.addWidget(output_label)
output_layout.addWidget(output_entry)
output_layout.addWidget(output_button)
layout.addLayout(output_layout)

# Meters per cm entry
meters_per_cm_layout = QHBoxLayout()
meters_per_cm_label = QLabel("米轉git add .公分：")
meters_per_cm_entry = QLineEdit("100")
meters_per_cm_layout.addWidget(meters_per_cm_label)
meters_per_cm_layout.addWidget(meters_per_cm_entry)
layout.addLayout(meters_per_cm_layout)

# Scale factor entry
scale_factor_layout = QHBoxLayout()
scale_factor_label = QLabel("縮放比例：")
scale_factor_entry = QLineEdit("0.05")
scale_factor_layout.addWidget(scale_factor_label)
scale_factor_layout.addWidget(scale_factor_entry)
layout.addLayout(scale_factor_layout)

# Convert button
convert_button = QPushButton("開始轉換")
convert_button.clicked.connect(convert_gpx_to_svg)
layout.addWidget(convert_button)

window.setLayout(layout)
window.show()

sys.exit(app.exec())
