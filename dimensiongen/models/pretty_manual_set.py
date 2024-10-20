import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QFileDialog, QMessageBox
)
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt, QPoint
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
        self.point_front_labels = []  # Labels for points in the front image
        self.point_side_labels = []  # Labels for points in the side image
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

        # Initialize point labels for front and side images
        self.point_front_labels = [
            "Front Point 1", "Front Point 2", "Front Point 3"
        ]
        self.point_side_labels = [
            "Side Point 1", "Side Point 2", "Side Point 3"
        ]

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

    def load_side_image(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Side Image", "", "Image Files (*.png *.jpg *.bmp)")
        if filename:
            self.side_image = cv2.imread(filename)
            self.current_image = self.side_image.copy()
            self.current_points = self.side_points
            self.current_point_labels = self.point_side_labels
            self.point_idx_side = 0
            self.display_image()

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
                point_idx = self.point_idx_front if self.current_image is self.front_image else self.point_idx_side
                if point_idx < len(self.current_point_labels):
                    label = self.current_point_labels[point_idx]
                    cv2.putText(self.current_image, label, (img_x + 10, img_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                (0, 255, 0), 1)
                    self.current_points.append((img_x, img_y))
                    if self.current_image is self.front_image:
                        self.point_idx_front += 1
                    else:
                        self.point_idx_side += 1
                else:
                    QMessageBox.information(self, "Info", "All points have been placed.")
            self.display_image()

    def next_point(self):
        current_point_idx = self.point_idx_front if self.current_image is self.front_image else self.point_idx_side
        if current_point_idx < len(self.current_point_labels):
            QMessageBox.information(self, "Next Point",
                                    f"Select point for: {self.current_point_labels[current_point_idx]}")
        else:
            QMessageBox.information(self, "Info", "All points have been placed.")

    def calculate_measurements(self):
        """Calculates distances between pairs of points."""
        if len(self.current_points) >= 2:
            # Example calculation between each pair of points
            for i in range(0, len(self.current_points) - 1, 2):
                p1 = self.current_points[i]
                p2 = self.current_points[i + 1]
                distance = self.calculate_distance(p1, p2)
                label1 = self.current_point_labels[i]
                label2 = self.current_point_labels[i + 1]
                print(f"Distance between {label1} and {label2}: {distance:.2f} pixels")
            # Optionally, save to CSV
            self.export_to_csv("output_measurements.csv")
            QMessageBox.information(self, "Calculations Complete", "Measurements calculated and saved.")
        else:
            QMessageBox.warning(self, "Warning", "Not enough points to calculate measurements.")

    def calculate_distance(self, p1, p2):
        """Calculate the Euclidean distance between two points."""
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def export_to_csv(self, filename):
        """Export the point coordinates and distances to a CSV file."""
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Point Label", "X Coordinate", "Y Coordinate"])
            for i, (x, y) in enumerate(self.current_points):
                writer.writerow([self.current_point_labels[i], x, y])
        print(f"Results exported to {filename}")

def main():
    app = QApplication(sys.argv)
    window = MeasurementTool()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
