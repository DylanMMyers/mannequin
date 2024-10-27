import sys
import cv2
import numpy as np
import math
import csv
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QFileDialog, QMessageBox, QInputDialog
)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt

class MeasurementTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Measurement Tool")

        # Variables to hold images, points, and scale factor
        self.front_image = None
        self.current_image = None
        self.front_points = []
        self.side_points = []
        self.point_front_labels = ["testt", "test2"] 
        """[
            "Top of Head", "Left Shoulder", "Right Shoulder", "Chest", "Waist",
            "Left Hip", "Right Hip", "Left Knee", "Right Knee", "Left Ankle",
            "Right Ankle", "Bottom of Feet"
        ]"""
        self.point_side_labels = ["test", "test56356"]
        self.point_idx = 0
        self.user_height = None  # Store user's height
        self.scale_factor = None  # Scale factor (inches per pixel)
        self.iter = 0

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.image_label = QLabel()
        self.image_label.setFixedSize(800, 600)
        self.image_label.setStyleSheet("background-color: black;")

        load_front_btn = QPushButton("Load Image")
        load_front_btn.clicked.connect(self.load_front_image)

        next_point_btn = QPushButton("Next Point")
        next_point_btn.clicked.connect(self.next_point)

        calculate_btn = QPushButton("Calculate Measurements")
        calculate_btn.clicked.connect(self.calculate_measurements)

        button_layout = QHBoxLayout()
        button_layout.addWidget(load_front_btn)
        button_layout.addWidget(next_point_btn)
        button_layout.addWidget(calculate_btn)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.image_label)
        main_layout.addLayout(button_layout)

        central_widget.setLayout(main_layout)
        self.image_label.mousePressEvent = self.mouse_press_event

    def load_front_image(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Front Image", "", "Image Files (*.png *.jpg *.bmp)")
        if filename:
            self.front_image = cv2.imread(filename)
            self.current_image = self.front_image.copy()
            self.front_points.clear()
            self.point_idx = 0
            self.display_image()
            self.get_user_height()  # Prompt user for their height
            self.next_point()

    def get_user_height(self):
        text, ok = QInputDialog.getText(self, 'Input Height', 'Enter your height in inches:')
        if ok and text:
            try:
                self.user_height = float(text)
            except ValueError:
                QMessageBox.warning(self, "Invalid Input", "Please enter a valid number.")
                self.get_user_height()

    def display_image(self):
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
            label_size = self.image_label.size()
            pixmap_size = self.image_label.pixmap().size()
            ratio = pixmap_size.width() / self.current_image.shape[1]
            img_x = int(x / ratio)
            img_y = int(y / ratio)
            cv2.circle(self.current_image, (img_x, img_y), 5, (0, 0, 255), -1)
              
            if self.iter == 0:
                if self.point_idx < len(self.point_front_labels):
                    label = self.point_front_labels[self.point_idx]
                    cv2.putText(self.current_image, label, (img_x + 10, img_y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    self.front_points.append((img_x, img_y))
                    self.point_idx += 1
                    self.display_image()
                    self.next_point()
            else:
                if self.point_idx < len(self.point_side_labels):
                    label = self.point_side_labels[self.point_idx]
                    cv2.putText(self.current_image, label, (img_x + 10, img_y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    self.side_points.append((img_x, img_y))
                    self.point_idx += 1
                    self.display_image()
                    self.next_point()

    def next_point(self):
        if self.iter == 0:
            if self.point_idx < len(self.point_front_labels):
                QMessageBox.information(self, "Next Point", f"Select point for: {self.point_front_labels[self.point_idx]}")
            else:
                QMessageBox.information(self, "Info", "All points have been placed.")
        else:
            if self.point_idx < len(self.point_front_labels):
                QMessageBox.information(self, "Next Point", f"Select point for: {self.point_side_labels[self.point_idx]}")
            else:
                QMessageBox.information(self, "Info", "All points have been placed.")

    def calculate_measurements(self):
        pointlen = None
        if self.iter == 0:
            pointlen = len(self.front_points)
        else:
            pointlen = len(self.side_points)
        if pointlen >= 2:
            pixel_height = None
            if self.iter == 0:
                top_of_head = self.front_points[0]
                bottom_of_feet = self.front_points[-1]
                pixel_height = self.calculate_distance(top_of_head, bottom_of_feet)
            else:
                top_of_head = self.side_points[0]
                bottom_of_feet = self.side_points[-1]
                pixel_height = self.calculate_distance(top_of_head, bottom_of_feet)

            if self.user_height is not None:
                self.scale_factor = self.user_height / pixel_height
                measurements = []
                if self.iter == 0:
                    for i in range(1, len(self.front_points) - 1):
                        p1 = self.front_points[i]
                        p2 = self.front_points[i + 1]
                        distance_pixels = self.calculate_distance(p1, p2)
                        distance_inches = distance_pixels * self.scale_factor
                        label1 = self.point_front_labels[i]
                        label2 = self.point_front_labels[i + 1]
                        measurements.append((f"{label1} to {label2}", distance_inches))
                        print(f"Distance between {label1} and {label2}: {distance_inches:.2f} inches")
                else:
                    for i in range(1, len(self.side_points) - 1):
                        p1 = self.side_points[i]
                        p2 = self.side_points[i + 1]
                        distance_pixels = self.calculate_distance(p1, p2)
                        distance_inches = distance_pixels * self.scale_factor
                        label1 = self.point_side_labels[i]
                        label2 = self.point_side_labels[i + 1]
                        measurements.append((f"{label1} to {label2}", distance_inches))
                        print(f"Distance between {label1} and {label2}: {distance_inches:.2f} inches")

                self.export_to_csv(f"output_measurements{self.iter}.csv", measurements)
                self.iter += 1
                self.point_idx = 0
                QMessageBox.information(self, "Calculations Complete", "Measurements calculated and saved.")
            else:
                QMessageBox.warning(self, "Warning", "User height is not set.")
        else:
            QMessageBox.warning(self, "Warning", "Not enough points to calculate measurements.")

    def calculate_distance(self, p1, p2):
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    def export_to_csv(self, filename, measurements):
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Point Label", "X Coordinate", "Y Coordinate"])
            if self.iter == 0:
                for i, (x, y) in enumerate(self.front_points):
                    writer.writerow([self.point_front_labels[i], x, y])
            else:
                for i, (x, y) in enumerate(self.side_points):
                    writer.writerow([self.point_side_labels[i], x, y])

            writer.writerow([])
            writer.writerow(["Measurement", "Distance (inches)"])
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
