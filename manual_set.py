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
        self.side_image = None
        self.current_image = None
        self.front_points = []
        self.side_points = []

        # Updated point labels
        self.point_front_labels = [
            "Top of Head", "Left Chest", "Right Chest", "Left Waist", "Right Waist", "Bottom of Feet"
        ]
        self.point_side_labels = [
            "Top of Head", "Chest Front", "Chest Back", "Waist Front", "Waist Back", "Bottom of Feet"
        ]

        self.point_idx = 0
        self.image_type = 'front'  # To track which image is being processed

        # Store user's measurements
        self.user_height = None  # Height in cm
        self.gender = None       # User's gender

        self.scale_factor = None  # Scale factor (cm per pixel)

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.image_label = QLabel()
        self.image_label.setFixedSize(800, 600)
        self.image_label.setStyleSheet("background-color: black;")

        load_front_btn = QPushButton("Load Front Image")
        load_front_btn.clicked.connect(self.load_front_image)

        load_side_btn = QPushButton("Load Side Image")
        load_side_btn.clicked.connect(self.load_side_image)

        next_point_btn = QPushButton("Next Point")
        next_point_btn.clicked.connect(self.next_point)

        calculate_btn = QPushButton("Calculate Measurements")
        calculate_btn.clicked.connect(self.calculate_measurements)

        button_layout = QHBoxLayout()
        button_layout.addWidget(load_front_btn)
        button_layout.addWidget(load_side_btn)
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
            self.image_type = 'front'
            self.display_image()
            if self.user_height is None:
                self.get_user_height()  # Prompt user for their height
            if self.gender is None:
                self.get_user_gender()  # Prompt user for their gender
            self.next_point()

    def load_side_image(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Side Image", "", "Image Files (*.png *.jpg *.bmp)")
        if filename:
            self.side_image = cv2.imread(filename)
            self.current_image = self.side_image.copy()
            self.side_points.clear()
            self.point_idx = 0
            self.image_type = 'side'
            self.display_image()
            if self.user_height is None:
                self.get_user_height()  # Prompt user for their height
            if self.gender is None:
                self.get_user_gender()  # Prompt user for their gender
            self.next_point()

    def get_user_height(self):
        text, ok = QInputDialog.getText(self, 'Input Height', 'Enter your height in cm:')
        if ok and text:
            try:
                self.user_height = float(text)
            except ValueError:
                QMessageBox.warning(self, "Invalid Input", "Please enter a valid number for height.")
                self.get_user_height()
        else:
            QMessageBox.warning(self, "Input Required", "Height is required.")
            self.get_user_height()

    def get_user_gender(self):
        items = ("Male", "Female")
        item, ok = QInputDialog.getItem(self, "Select Gender", "Gender:", items, 0, False)
        if ok and item:
            self.gender = item
        else:
            QMessageBox.warning(self, "Input Required", "Gender selection is required.")
            self.get_user_gender()

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
            pixmap = self.image_label.pixmap()
            if pixmap is None:
                return
            pixmap_size = pixmap.size()
            label_size = self.image_label.size()
            ratio_w = self.current_image.shape[1] / pixmap_size.width()
            ratio_h = self.current_image.shape[0] / pixmap_size.height()
            img_x = int(x * ratio_w)
            img_y = int(y * ratio_h)
            cv2.circle(self.current_image, (img_x, img_y), 5, (0, 0, 255), -1)

            if self.image_type == 'front':
                if self.point_idx < len(self.point_front_labels):
                    label = self.point_front_labels[self.point_idx]
                    cv2.putText(self.current_image, label, (img_x + 10, img_y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    self.front_points.append((img_x, img_y))
                    self.point_idx += 1
                    self.display_image()
                    self.next_point()
            elif self.image_type == 'side':
                if self.point_idx < len(self.point_side_labels):
                    label = self.point_side_labels[self.point_idx]
                    cv2.putText(self.current_image, label, (img_x + 10, img_y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    self.side_points.append((img_x, img_y))
                    self.point_idx += 1
                    self.display_image()
                    self.next_point()

    def next_point(self):
        if self.image_type == 'front':
            if self.point_idx < len(self.point_front_labels):
                QMessageBox.information(self, "Next Point", f"Select point for: {self.point_front_labels[self.point_idx]}")
            else:
                QMessageBox.information(self, "Info", "All front points have been placed.")
        elif self.image_type == 'side':
            if self.point_idx < len(self.point_side_labels):
                QMessageBox.information(self, "Next Point", f"Select point for: {self.point_side_labels[self.point_idx]}")
            else:
                QMessageBox.information(self, "Info", "All side points have been placed.")

    def calculate_measurements(self):
        if self.user_height is None:
            QMessageBox.warning(self, "Warning", "User height is not set.")
            return

        if self.gender is None:
            QMessageBox.warning(self, "Warning", "User gender is not set.")
            return

        if len(self.front_points) < len(self.point_front_labels):
            QMessageBox.warning(self, "Warning", "Not all front points have been selected.")
            return

        if len(self.side_points) < len(self.point_side_labels):
            QMessageBox.warning(self, "Warning", "Not all side points have been selected.")
            return

        # Calculate scale factors for front and side images
        front_pixel_height = self.calculate_distance(self.front_points[0], self.front_points[-1])
        side_pixel_height = self.calculate_distance(self.side_points[0], self.side_points[-1])
        avg_pixel_height = (front_pixel_height + side_pixel_height) / 2

        self.scale_factor = self.user_height / avg_pixel_height  # cm per pixel

        # Calculate chest measurements
        chest_width_pixels = self.calculate_distance(self.front_points[1], self.front_points[2])
        chest_depth_pixels = self.calculate_distance(self.side_points[1], self.side_points[2])
        chest_width_cm = chest_width_pixels * self.scale_factor
        chest_depth_cm = chest_depth_pixels * self.scale_factor

        chest_circumference = self.calculate_ellipse_circumference(chest_width_cm, chest_depth_cm) * 1.1

        # Calculate waist measurements
        waist_width_pixels = self.calculate_distance(self.front_points[3], self.front_points[4])
        waist_depth_pixels = self.calculate_distance(self.side_points[3], self.side_points[4])
        waist_width_cm = waist_width_pixels * self.scale_factor
        waist_depth_cm = waist_depth_pixels * self.scale_factor

        waist_circumference = self.calculate_ellipse_circumference(waist_width_cm, waist_depth_cm) * 1.1

        # Collect measurements
        measurements = []
        measurements.append(("Chest Circumference", chest_circumference))
        measurements.append(("Waist Circumference", waist_circumference))

        # Estimate other measurements
        estimated_measurements = self.estimate_measurements(chest_circumference, waist_circumference)

        # Export to CSV
        self.export_to_csv("output_measurements.csv", measurements, estimated_measurements)

        QMessageBox.information(self, "Calculations Complete", "Measurements calculated and saved.")

    def calculate_distance(self, p1, p2):
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    def calculate_ellipse_circumference(self, width_cm, depth_cm):
        # Approximate circumference of an ellipse
        a = width_cm / 2  # Semi-major axis
        b = depth_cm / 2  # Semi-minor axis
        h = ((a - b) ** 2) / ((a + b) ** 2)
        circumference = math.pi * (a + b) * (1 + (3 * h) / (10 + math.sqrt(4 - 3 * h)))
        return circumference

    def estimate_measurements(self, chest_circumference, waist_circumference):
        measurements = {}

        if self.gender == 'Male':
            # Using the estimation formulas provided for males

            # Hip Circumference
            hip_circumference = ((chest_circumference + waist_circumference) / 2) * 1.05
            measurements['Hip Circumference'] = hip_circumference

            # Shoulder Width
            shoulder_width = (chest_circumference * 0.25) * 1.8
            measurements['Shoulder Width'] = shoulder_width

            # Sleeve Length
            sleeve_length = (self.user_height * 0.25) * 1.4
            measurements['Sleeve Length'] = sleeve_length

            # Inseam Length
            inseam_length = self.user_height * 0.45
            measurements['Inseam Length'] = inseam_length

            # Neck Circumference
            neck_circumference = chest_circumference * 0.37
            measurements['Neck Circumference'] = neck_circumference

            # Arm Length
            arm_length = self.user_height * 0.28
            measurements['Arm Length'] = arm_length

            # Thigh Circumference
            thigh_circumference = waist_circumference * 0.68
            measurements['Thigh Circumference'] = thigh_circumference

            # Torso Length
            torso_length = self.user_height * 0.27
            measurements['Torso Length'] = torso_length

            # Leg Length
            leg_length = self.user_height * 0.53
            measurements['Leg Length'] = leg_length

        elif self.gender == 'Female':
            # Adjusted estimation formulas for females

            # Hip Circumference (generally larger in females)
            hip_circumference = ((chest_circumference + waist_circumference) / 2) * 1.15
            measurements['Hip Circumference'] = hip_circumference

            # Shoulder Width (generally narrower in females)
            shoulder_width = (chest_circumference * 0.25) * 1.6
            measurements['Shoulder Width'] = shoulder_width

            # Sleeve Length (slightly shorter)
            sleeve_length = (self.user_height * 0.24) * 1.4
            measurements['Sleeve Length'] = sleeve_length

            # Inseam Length (slightly shorter)
            inseam_length = self.user_height * 0.44
            measurements['Inseam Length'] = inseam_length

            # Neck Circumference (slightly smaller)
            neck_circumference = chest_circumference * 0.35
            measurements['Neck Circumference'] = neck_circumference

            # Arm Length (slightly shorter)
            arm_length = self.user_height * 0.27
            measurements['Arm Length'] = arm_length

            # Thigh Circumference (slightly larger)
            thigh_circumference = waist_circumference * 0.75
            measurements['Thigh Circumference'] = thigh_circumference

            # Torso Length (slightly longer)
            torso_length = self.user_height * 0.28
            measurements['Torso Length'] = torso_length

            # Leg Length (slightly shorter)
            leg_length = self.user_height * 0.52
            measurements['Leg Length'] = leg_length

        return measurements

    def export_to_csv(self, filename, measurements, estimated_measurements):
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)

            writer.writerow(["User Information"])
            writer.writerow(["Gender", self.gender])
            writer.writerow(["Height (cm)", f"{self.user_height:.2f}"])

            writer.writerow([])
            writer.writerow(["Front Image Points"])
            writer.writerow(["Point Label", "X Coordinate", "Y Coordinate"])
            for i, (x, y) in enumerate(self.front_points):
                writer.writerow([self.point_front_labels[i], x, y])

            writer.writerow([])
            writer.writerow(["Side Image Points"])
            writer.writerow(["Point Label", "X Coordinate", "Y Coordinate"])
            for i, (x, y) in enumerate(self.side_points):
                writer.writerow([self.point_side_labels[i], x, y])

            writer.writerow([])
            writer.writerow(["Measured Circumferences", "Value (cm)"])
            for measurement in measurements:
                writer.writerow([measurement[0], f"{measurement[1]:.2f}"])

            writer.writerow([])
            writer.writerow(["Estimated Measurements", "Value (cm)"])
            for key, value in estimated_measurements.items():
                writer.writerow([key, f"{value:.2f}"])

        print(f"Results exported to {filename}")

def main():
    app = QApplication(sys.argv)
    window = MeasurementTool()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
