import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QFileDialog, QMessageBox
)
from PyQt5.QtGui  import QImage, QPixmap
from PyQt5.QtCore import Qt
import math
import csv

class MeasurementTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Measurement Tool")

        # Variables to hold images and points for front and side images
        self.front_image = None
        self.side_image = None
        self.current_image = None  # Current image being displayed
        self.front_points = []
        self.side_points = []
        self.point_front_labels = ["Left Shoulder", "Right Shoulder", "Chest",
                                   "Waist", "Left Hip", "Right Hip", "Left Knee", "Right Knee",
                                   "Left Ankle", "Right Ankle"]  # Labels for points in the front image
        self.point_side_labels = ["Neck", "Shoulder", "Elbow", "Wrist",
                                  "Waist", "Hip", "Knee", "Ankle"]  # Labels for points in the side image
        self.point_idx_front = 0  # Index for points in the front image
        self.point_idx_side = 0   # Index for points in the side image
        self.current_point_labels = []  # Current set of point labels
        self.current_points = []  # Current set of points (either front or side)

        # UI Setup
        self.init_ui()

    def init_ui(self):
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Image display area
        self.image_label = QLabel()
        self.image_label.setFixedSize(800, 600)
        self.image_label.setStyleSheet("background-color: black;")

        # Buttons and controls
        load_front_btn = QPushButton("Load Front Image")
        load_front_btn.clicked.connect(self.load_front_image)

        load_side_btn = QPushButton("Load Side Image")
        load_side_btn.clicked.connect(self.load_side_image)

        next_point_btn = QPushButton("Next Point")
        next_point_btn.clicked.connect(self.next_point)

        calculate_btn = QPushButton("Calculate Measurements")
        calculate_btn.clicked.connect(self.calculate_measurements)

        # Layouts
        button_layout = QHBoxLayout()
        button_layout.addWidget(load_front_btn)
        button_layout.addWidget(load_side_btn)
        button_layout.addWidget(next_point_btn)
        button_layout.addWidget(calculate_btn)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.image_label)
        main_layout.addLayout(button_layout)

        central_widget.setLayout(main_layout)

        # Set up mouse event handling
        self.image_label.mousePressEvent = self.mouse_press_event

    def load_front_image(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Front Image", "", "Image Files (*.png *.jpg *.bmp)")
        if filename:
            self.front_image = cv2.imread(filename)
            self.current_image = self.front_image.copy()
            self.current_points = self.front_points
            self.current_point_labels = self.point_front_labels
            self.point_idx_front = 0
            self.display_image()
            self.next_point()  # Prompt the user

    def load_side_image(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Side Image", "", "Image Files (*.png *.jpg *.bmp)")
        if filename:
            self.side_image = cv2.imread(filename)
            self.current_image = self.side_image.copy()
            self.current_points = self.side_points
            self.current_point_labels = self.point_side_labels
            self.point_idx_side = 0
            self.display_image()
            self.next_point()  # Prompt the user

    def display_image(self):
        """Convert the current image to QPixmap and display it."""
        if self.current_image is not None:
            height, width, channel = self.current_image.shape
            bytes_per_line = 3 * width
            q_img = QImage(self.current_image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
            pixmap = QPixmap.fromImage(q_img)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))

    def mouse_press_event(self, event):
        if event.button() == Qt.LeftButton and self.current_image is not None:
            x = event.pos().x()
            y = event.pos().y()

            # Map the click position to the image coordinates
            label_size = self.image_label.size()
            pixmap_size = self.image_label.pixmap().size()
            ratio = pixmap_size.width() / self.current_image.shape[1]

            img_x = int(x / ratio)
            img_y = int(y / ratio)

            # Draw a circle at the clicked point
            cv2.circle(self.current_image, (img_x, img_y), 5, (0, 0, 255), -1)

            # Draw the label
            if len(self.current_point_labels) > 0:
                if self.current_image is self.front_image:
                    point_idx = self.point_idx_front
                else:
                    point_idx = self.point_idx_side

                if point_idx < len(self.current_point_labels):
                    label = self.current_point_labels[point_idx]
                    cv2.putText(
                        self.current_image, label, (img_x + 10, img_y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1
                    )
                    self.current_points.append((img_x, img_y))

                    # Increment the correct point index
                    if self.current_image is self.front_image:
                        self.point_idx_front += 1
                    else:
                        self.point_idx_side += 1

                    self.display_image()

                    # Prompt for the next point
                    self.next_point()
                else:
                    QMessageBox.information(self, "Info", "All points have been placed.")
            else:
                QMessageBox.warning(self, "Warning", "No point labels are available.")

    def next_point(self):
        if self.current_image is self.front_image:
            current_point_idx = self.point_idx_front
        else:
            current_point_idx = self.point_idx_side

        if current_point_idx < len(self.current_point_labels):
            QMessageBox.information(
                self, "Next Point",
                f"Select point for: {self.current_point_labels[current_point_idx]}"
            )
        else:
            QMessageBox.information(self, "Info", "All points have been placed.")

    def calculate_measurements(self):
        """Calculates distances between pairs of points."""
        measurements = []

        # Calculate measurements for front image
        if len(self.front_points) >= 2:
            for i in range(len(self.front_points) - 1):
                p1 = self.front_points[i]
                p2 = self.front_points[i + 1]
                distance = self.calculate_distance(p1, p2)
                label1 = self.point_front_labels[i]
                label2 = self.point_front_labels[i + 1]
                measurements.append((f"{label1} to {label2}", distance))
                print(f"Front - Distance between {label1} and {label2}: {distance:.2f} pixels")

        # Calculate measurements for side image
        if len(self.side_points) >= 2:
            for i in range(len(self.side_points) - 1):
                p1 = self.side_points[i]
                p2 = self.side_points[i + 1]
                distance = self.calculate_distance(p1, p2)
                label1 = self.point_side_labels[i]
                label2 = self.point_side_labels[i + 1]
                measurements.append((f"{label1} to {label2}", distance))
                print(f"Side - Distance between {label1} and {label2}: {distance:.2f} pixels")

        if measurements:
            self.export_to_csv("output_measurements.csv", measurements)
            QMessageBox.information(self, "Calculations Complete", "Measurements calculated and saved.")
        else:
            QMessageBox.warning(self, "Warning", "Not enough points to calculate measurements.")

    def calculate_distance(self, p1, p2):
        """Calculate the Euclidean distance between two points."""
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    def export_to_csv(self, filename, measurements):
        """Export the point coordinates and distances to a CSV file."""
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Point Label", "X Coordinate", "Y Coordinate"])

            # Write front image points
            for i, (x, y) in enumerate(self.front_points):
                writer.writerow([self.point_front_labels[i], x, y])

            # Write side image points
            for i, (x, y) in enumerate(self.side_points):
                writer.writerow([self.point_side_labels[i], x, y])

            # Write measurements
            writer.writerow([])
            writer.writerow(["Measurement", "Distance (pixels)"])
            for measurement in measurements:
                writer.writerow([measurement[0], f"{measurement[1]:.2f}"])

        print(f"Results exported to {filename}")

def main():
    app = QApplication(sys.argv)
    window = MeasurementTool()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
