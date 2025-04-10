import sys
import cv2
import numpy as np
import math
import csv
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QFileDialog, QMessageBox, QInputDialog
)
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QPoint

class IntegratedMeasurementTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Body Measurement Tool")
        
        # Image and point variables
        self.front_image = None
        self.side_image = None
        self.current_image = None
        self.front_points = []
        self.side_points = []
        self.current_points = []
        
        # User measurements
        self.user_height = None
        self.gender = None
        self.scale_factor = None
        
        # Drag and drop variables
        self.dragging = False
        self.drag_point_index = -1
        
        # Point labels
        self.point_front_labels = [
            "Top of Head", "Left Chest", "Right Chest",
            "Left Waist", "Right Waist", "Bottom of Feet"
        ]
        self.point_side_labels = [
            "Top of Head", "Chest Front", "Chest Back",
            "Waist Front", "Waist Back", "Bottom of Feet"
        ]
        
        self.current_point_labels = []
        self.point_idx = 0
        self.image_type = 'front'
        
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Image display
        self.image_label = QLabel()
        self.image_label.setFixedSize(800, 600)
        self.image_label.setStyleSheet("background-color: black;")
        
        # Buttons
        load_front_btn = QPushButton("Load Front Image")
        load_side_btn = QPushButton("Load Side Image")
        next_point_btn = QPushButton("Next Point")
        calculate_btn = QPushButton("Calculate Measurements")
        
        load_front_btn.clicked.connect(self.load_front_image)
        load_side_btn.clicked.connect(self.load_side_image)
        next_point_btn.clicked.connect(self.next_point)
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
        
        # Mouse events
        self.image_label.mousePressEvent = self.mouse_press_event
        self.image_label.mouseMoveEvent = self.mouse_move_event
        self.image_label.mouseReleaseEvent = self.mouse_release_event
    
    def calculate_distance(self, p1, p2):
        if not p1 or not p2:
            return 0
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
        
    def display_image(self):
        if self.current_image is not None:
            height, width, channel = self.current_image.shape
            bytes_per_line = 3 * width
            q_img = QImage(self.current_image.data, width, height, 
                        bytes_per_line, QImage.Format_RGB888).rgbSwapped()
            pixmap = QPixmap.fromImage(q_img)
            self.image_label.setPixmap(pixmap.scaled(
                self.image_label.size(), Qt.KeepAspectRatio))
            self.draw_points()
            
    def draw_points(self):
        if not self.image_label.pixmap():
            return
        painter = QPainter(self.image_label.pixmap())
        painter.setRenderHint(QPainter.Antialiasing)
        
        for i, point in enumerate(self.current_points):
            painter.setPen(QPen(QColor(255, 0, 0), 3))
            painter.drawEllipse(QPoint(*point), 5, 5)
            painter.setPen(QColor(0, 255, 0))
            label = (self.point_front_labels if self.image_type == 'front' 
                    else self.point_side_labels)[i]
            painter.drawText(point[0] + 10, point[1] - 10, label)
        painter.end()
        self.image_label.update()
        
    def next_point(self):
        if self.current_image is None:
            return
            
        current_labels = self.point_front_labels if self.image_type == 'front' else self.point_side_labels
        current_points = self.front_points if self.image_type == 'front' else self.side_points
        
        if len(current_points) < len(current_labels):
            QMessageBox.information(
                self, 
                "Next Point", 
                f"Select point for: {current_labels[len(current_points)]}"
            )
        else:
            QMessageBox.information(
                self, 
                "Info", 
                f"All {self.image_type} points have been placed."
            )

    def load_front_image(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Front Image", "", 
                                                "Image Files (*.png *.jpg *.bmp)")
        if filename:
            self.front_image = cv2.imread(filename)
            self.current_image = self.front_image.copy()
            self.current_points = self.front_points
            self.current_point_labels = self.point_front_labels
            self.image_type = 'front'
            self.point_idx = 0
            
            if self.user_height is None:
                self.get_user_height()
            if self.gender is None:
                self.get_user_gender()
                
            self.display_image()
            self.next_point()

    def load_side_image(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Side Image", "", 
                                                "Image Files (*.png *.jpg *.bmp)")
        if filename:
            self.side_image = cv2.imread(filename)
            self.current_image = self.side_image.copy()
            self.current_points = self.side_points
            self.current_point_labels = self.point_side_labels
            self.image_type = 'side'
            self.point_idx = 0
            
            self.display_image()
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

    def mouse_press_event(self, event):
        if event.button() == Qt.LeftButton and self.current_image is not None:
            x = event.pos().x()
            y = event.pos().y()
            
            # Check if clicking near existing point for drag
            for i, point in enumerate(self.current_points):
                if math.sqrt((point[0] - x)**2 + (point[1] - y)**2) < 10:
                    self.dragging = True
                    self.drag_point_index = i
                    return

            # Add new point if not dragging
            if len(self.current_points) < len(self.current_point_labels):
                self.current_points.append((x, y))
                self.point_idx += 1
                self.display_image()
                self.next_point()

    def calculate_measurements(self):
        if not self._validate_measurements():
            return

        # Calculate scale factors
        front_pixel_height = self.calculate_distance(self.front_points[0], self.front_points[-1])
        side_pixel_height = self.calculate_distance(self.side_points[0], self.side_points[-1])
        avg_pixel_height = (front_pixel_height + side_pixel_height) / 2
        self.scale_factor = self.user_height / avg_pixel_height

        # Calculate primary measurements
        chest_width_pixels = self.calculate_distance(self.front_points[1], self.front_points[2])
        chest_depth_pixels = self.calculate_distance(self.side_points[1], self.side_points[2])
        chest_width_cm = chest_width_pixels * self.scale_factor
        chest_depth_cm = chest_depth_pixels * self.scale_factor
        chest_circumference = self.calculate_ellipse_circumference(chest_width_cm, chest_depth_cm) * 1.1

        waist_width_pixels = self.calculate_distance(self.front_points[3], self.front_points[4])
        waist_depth_pixels = self.calculate_distance(self.side_points[3], self.side_points[4])
        waist_width_cm = waist_width_pixels * self.scale_factor
        waist_depth_cm = waist_depth_pixels * self.scale_factor
        waist_circumference = self.calculate_ellipse_circumference(waist_width_cm, waist_depth_cm) * 1.2

        # Collect and export measurements
        measurements = [
            ("Chest Circumference", chest_circumference),
            ("Waist Circumference", waist_circumference)
        ]
        estimated_measurements = self.estimate_measurements(chest_circumference, waist_circumference)
        self.export_to_csv("output_measurements.csv", measurements, estimated_measurements)
        QMessageBox.information(self, "Calculations Complete", "Measurements calculated and saved.")

    def _validate_measurements(self):
        if self.user_height is None:
            QMessageBox.warning(self, "Warning", "User height is not set.")
            return False
        if self.gender is None:
            QMessageBox.warning(self, "Warning", "User gender is not set.")
            return False
        if len(self.front_points) < len(self.point_front_labels):
            QMessageBox.warning(self, "Warning", "Not all front points have been selected.")
            return False
        if len(self.side_points) < len(self.point_side_labels):
            QMessageBox.warning(self, "Warning", "Not all side points have been selected.")
            return False
        return True

    def calculate_ellipse_circumference(self, width_cm, depth_cm):
        a = width_cm / 2
        b = depth_cm / 2
        h = ((a - b) ** 2) / ((a + b) ** 2)
        return math.pi * (a + b) * (1 + (3 * h) / (10 + math.sqrt(4 - 3 * h)))

    def estimate_measurements(self, chest_circumference, waist_circumference):
        measurements = {}
        if self.gender == 'Male':
            measurements.update({
                'Hip Circumference': ((chest_circumference + waist_circumference) / 2) * 1.05,
                'Shoulder Width': (chest_circumference * 0.25) * 1.8,
                'Sleeve Length': (self.user_height * 0.25) * 1.4,
                'Inseam Length': self.user_height * 0.45,
                'Neck Circumference': chest_circumference * 0.37,
                'Arm Length': self.user_height * 0.28,
                'Thigh Circumference': waist_circumference * 0.7,
                'Torso Length': self.user_height * 0.27,
                'Leg Length': self.user_height * 0.53
            })
        else:  # Female
            measurements.update({
                'Hip Circumference': ((chest_circumference + waist_circumference) / 2) * 1.15,
                'Shoulder Width': (chest_circumference * 0.25) * 1.75,
                'Sleeve Length': (self.user_height * 0.24) * 1.4,
                'Inseam Length': self.user_height * 0.46,
                'Neck Circumference': chest_circumference * 0.39,
                'Arm Length': self.user_height * 0.30,
                'Thigh Circumference': waist_circumference * 0.75,
                'Torso Length': self.user_height * 0.28,
                'Leg Length': self.user_height * 0.55
            })
        return measurements
    def mouse_move_event(self, event):
        if self.dragging and self.current_image is not None:
            x = event.pos().x()
            y = event.pos().y()
            self.current_points[self.drag_point_index] = (x, y)
            self.display_image()
            self.draw_points()

    def mouse_release_event(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.drag_point_index = -1

    def export_to_csv(self, filename, measurements, estimated_measurements):
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            
            # User Information
            writer.writerow(["User Information"])
            writer.writerow(["Gender", self.gender])
            writer.writerow(["Height (cm)", f"{self.user_height:.2f}"])
            writer.writerow([])
            
            # Front Image Points
            writer.writerow(["Front Image Points"])
            writer.writerow(["Point Label", "X Coordinate", "Y Coordinate"])
            for i, (x, y) in enumerate(self.front_points):
                writer.writerow([self.point_front_labels[i], x, y])
            writer.writerow([])
            
            # Side Image Points
            writer.writerow(["Side Image Points"])
            writer.writerow(["Point Label", "X Coordinate", "Y Coordinate"])
            for i, (x, y) in enumerate(self.side_points):
                writer.writerow([self.point_side_labels[i], x, y])
            writer.writerow([])
            
            # Measurements
            writer.writerow(["Measured Circumferences", "Value (cm)"])
            for measurement in measurements:
                writer.writerow([measurement[0], f"{measurement[1]:.2f}"])
            writer.writerow([])
            
            # Estimated Measurements
            writer.writerow(["Estimated Measurements", "Value (cm)"])
            for key, value in estimated_measurements.items():
                writer.writerow([key, f"{value:.2f}"])

def main():
    app = QApplication(sys.argv)
    window = IntegratedMeasurementTool()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()