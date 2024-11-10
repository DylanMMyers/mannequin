import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QFileDialog, QMessageBox
)
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor
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
        self.point_idx_side = 0  # Index for points in the side image
        self.current_point_labels = []  # Current set of point labels
        self.current_points = []  # Current set of points (either front or side)

        # Variables for drag and drop
        self.dragging = False
        self.drag_point_index = -1

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
        self.image_label.mouseMoveEvent = self.mouse_move_event
        self.image_label.mouseReleaseEvent = self.mouse_release_event

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
        if self.current_image is not None:
            height, width, channel = self.current_image.shape
            bytes_per_line = 3 * width
            q_img = QImage(self.current_image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
            self.pixmap = QPixmap.fromImage(q_img)
            self.image_label.setPixmap(self.pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))
            self.draw_points()

    def draw_points(self):
        if self.current_image is not None:
            painter = QPainter(self.image_label.pixmap())
            painter.setRenderHint(QPainter.Antialiasing)
            
            for i, (x, y) in enumerate(self.current_points):
                # Draw a larger, more distinct point
                painter.setPen(QPen(QColor(255, 0, 0), 3))  # Red outline
                painter.setBrush(QColor(255, 255, 0))  # Yellow fill
                painter.drawEllipse(QPoint(x, y), 8, 8)  # Larger radius
                
                # Draw the label
                painter.setPen(QColor(0, 255, 0))  # Green text
                painter.drawText(QPoint(x + 15, y - 15), self.current_point_labels[i])
            
            painter.end()
            self.image_label.update()

    def mouse_press_event(self, event):
        if event.button() == Qt.LeftButton and self.current_image is not None:
            x = event.pos().x()
            y = event.pos().y()
            
            # Check if the click is near an existing point
            for i, point in enumerate(self.current_points):
                if math.sqrt((point[0] - x)**2 + (point[1] - y)**2) < 10:
                    self.dragging = True
                    self.drag_point_index = i
                    return
            
            # If not dragging, add a new point
            if len(self.current_points) < len(self.current_point_labels):
                self.current_points.append((x, y))
                if self.current_image is self.front_image:
                    self.point_idx_front += 1
                else:
                    self.point_idx_side += 1
                self.display_image()

    def mouse_move_event(self, event):
        if self.dragging and self.current_image is not None:
            x = event.pos().x()
            y = event.pos().y()
            self.current_points[self.drag_point_index] = (x, y)
            self.display_image()

    def mouse_release_event(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.drag_point_index = -1

    def next_point(self):
        current_point_idx = self.point_idx_front if self.current_image is self.front_image else self.point_idx_side
        if current_point_idx < len(self.current_point_labels):
            QMessageBox.information(self, "Next Point",
                                    f"Select point for: {self.current_point_labels[current_point_idx]}")
        else:
            QMessageBox.information(self, "Info", "All points have been placed.")

    def calculate_measurements(self):
        if len(self.current_points) >= 2:
            for i in range(0, len(self.current_points) - 1, 2):
                p1 = self.current_points[i]
                p2 = self.current_points[i + 1]
                distance = self.calculate_distance(p1, p2)
                label1 = self.current_point_labels[i]
                label2 = self.current_point_labels[i + 1]
                print(f"Distance between {label1} and {label2}: {distance:.2f} pixels")

            self.export_to_csv("output_measurements.csv")
            QMessageBox.information(self, "Calculations Complete", "Measurements calculated and saved.")
        else:
            QMessageBox.warning(self, "Warning", "Not enough points to calculate measurements.")

    def calculate_distance(self, p1, p2):
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def export_to_csv(self, filename):
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