import cv2
import math
import csv

class MeasurementTool:
    def __init__(self):
        self.points = []
        self.side_points = []
        # Length/Front list
        self.point_labels = [
            "Shoulders (Left)", "Shoulders (Right)",
            "Chest (Left)", "Chest (Right)",
            "Hips (Left)", "Hips (Right)",
            "Waist (Left)", "Waist (Right)",
            "Left Upper Arm (Left)", "Left Upper Arm (Right)",
            "Left Elbow (Left)", "Left Elbow (Right)",
            "Left Lower Arm (Left)", "Left Lower Arm (Right)",
            "Right Upper Arm (Left)", "Right Upper Arm (Right)",
            "Right Elbow (Left)", "Right Elbow (Right)",
            "Right Lower Arm (Left)", "Right Lower Arm (Right)",
            "Left Upper Leg (Left)", "Left Upper Leg (Right)",
            "Left Knee (Left)", "Left Knee (Right)",
            "Left Lower Leg (Left)", "Left Lower Leg (Right)",
            "Right Upper Leg (Left)", "Right Upper Leg (Right)",
            "Right Knee (Left)", "Right Knee (Right)",
            "Right Lower Leg (Left)", "Right Lower Leg (Right)",
            "Head Length (Top)", "Head Length (Bottom)",
            "Arm Length (Left, Top)", "Arm Length (Left, Bottom)",
            "Arm Length (Right, Top)", "Arm Length (Right, Bottom)",
            "Torso Length (Top)", "Torso Length (Bottom)",
            "Leg Length (Left, Top)", "Leg Length (Left, Bottom)",
            "Leg Length (Right, Top)", "Leg Length (Right, Bottom)"
        ]

        # Depth/Side list
        self.side_point_labels = [
            "Shoulder (Left)", "Shoulder (Right)",
            "Mid Torso (Left)", "Mid Torso (Right)",
            "Hip (Left)", "Hip (Right)",
            "Waist (Left)", "Waist (Right)",
            "Upper Arm (Left)", "Upper Arm (Right)",
            "Left Elbow (Side)", "Right Elbow (Side)",
            "Lower Arm (Left)", "Lower Arm (Right)",
            "Upper Leg (Left)", "Upper Leg (Right)",
            "Knee (Left)", "Knee (Right)",
            "Lower Leg (Left)", "Lower Leg (Right)"
        ]

        self.point_idx = 0       # Track the current front point index
        self.side_point_idx = 0  # Track the current side point index
        self.image = None        # Front image
        self.side_image = None   # Side image
        self.display_width = 800 # Desired display width for consistent scaling

    def load_image(self, image_path):
        """Load and display the front image."""
        self.image = cv2.imread(image_path)
        if self.image is None:
            raise FileNotFoundError(f"Error: Could not load image from {image_path}")
        
        self.image = self.resize_image(self.image)
        self.show_image(self.image, "Front View", self.mouse_callback)
    
    def load_side_image(self, image_path):
        """Load and display the side image."""
        self.side_image = cv2.imread(image_path)
        if self.side_image is None:
            raise FileNotFoundError(f"Error: Could not load image from {image_path}")
        
        self.side_image = self.resize_image(self.side_image)
        self.show_image(self.side_image, "Side View", self.mouse_callback_side)

    def resize_image(self, img):
        """Resize the image while maintaining aspect ratio."""
        height, width = img.shape[:2]
        scale = self.display_width / width
        resized_image = cv2.resize(img, (self.display_width, int(height * scale)))
        return resized_image

    def show_image(self, img, window_name, callback_function):
        """Display the image and set mouse callback."""
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(window_name, callback_function)
        cv2.imshow(window_name, img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def mouse_callback(self, event, x, y, flags, params):
        """Callback function to handle mouse clicks for front view."""
        if event == cv2.EVENT_LBUTTONDOWN and self.point_idx < len(self.point_labels):
            self.points.append((x, y))
            label = self.point_labels[self.point_idx]
            print(f"Point {label} selected at: {x}, {y}")
            
            cv2.circle(self.image, (x, y), 5, (0, 255, 0), -1)
            cv2.putText(self.image, label, (x + 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            self.point_idx += 1
            cv2.imshow("Front View", self.image)

    def mouse_callback_side(self, event, x, y, flags, params):
        """Callback function to handle mouse clicks for side view."""
        if event == cv2.EVENT_LBUTTONDOWN and self.side_point_idx < len(self.side_point_labels):
            self.side_points.append((x, y))
            label = self.side_point_labels[self.side_point_idx]
            print(f"Point {label} selected at: {x}, {y}")
            
            cv2.circle(self.side_image, (x, y), 5, (0, 0, 255), -1)
            cv2.putText(self.side_image, label, (x + 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            self.side_point_idx += 1
            cv2.imshow("Side View", self.side_image)

    def calculate_distance(self, p1, p2):
        """Calculate the Euclidean distance between two points."""
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def draw_lines_and_display(self, img, points, labels, window_name):
        """Draw lines between points and display the image."""
        for i, (x, y) in enumerate(points):
            cv2.circle(img, (x, y), 5, (0, 255, 0), -1)
            cv2.putText(img, labels[i], (x + 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        for i in range(0, len(points) - 1, 2):
            cv2.line(img, points[i], points[i + 1], (255, 0, 0), 2)
        
        img_resized = self.resize_image(img)
        cv2.imshow(window_name, img_resized)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def calculate_and_display_results(self):
        """Calculate and display the distances for both front and side views."""
        if len(self.points) >= 2:
            print("\nFront View Distances:")
            for i in range(0, len(self.points) - 1, 2):
                p1, p2 = self.points[i], self.points[i + 1]
                distance = self.calculate_distance(p1, p2)
                print(f"Distance between {self.point_labels[i]} and {self.point_labels[i + 1]}: {distance:.2f} pixels")
            self.draw_lines_and_display(self.image, self.points, self.point_labels, "Front View with Lines")

        if len(self.side_points) >= 2:
            print("\nSide View Distances:")
            for i in range(0, len(self.side_points) - 1, 2):
                p1, p2 = self.side_points[i], self.side_points[i + 1]
                distance = self.calculate_distance(p1, p2)
                print(f"Depth between {self.side_point_labels[i]} and {self.side_point_labels[i + 1]}: {distance:.2f} pixels")
            self.draw_lines_and_display(self.side_image, self.side_points, self.side_point_labels, "Side View with Lines")

        # After calculation, export the results to a CSV file
        self.export_to_csv("points.csv")

    def export_to_csv(self, filename):
        """Export the point coordinates and distances to a CSV file."""
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["View", "Point Label", "X Coordinate", "Y Coordinate", "Distance (Pixels)"])

            # Write front view points and distances
            if len(self.points) >= 2:
                for i in range(len(self.points)):
                    x, y = self.points[i]
                    writer.writerow(["Front View", self.point_labels[i], x, y])
                for i in range(0, len(self.points) - 1, 2):
                    dist = self.calculate_distance(self.points[i], self.points[i + 1])
                    writer.writerow(["Front View", f"Distance {self.point_labels[i]} - {self.point_labels[i + 1]}", "", "", dist])

            # Write side view points and distances
            if len(self.side_points) >= 2:
                for i in range(len(self.side_points)):
                    x, y = self.side_points[i]
                    writer.writerow(["Side View", self.side_point_labels[i], x, y])
                for i in range(0, len(self.side_points) - 1, 2):
                    dist = self.calculate_distance(self.side_points[i], self.side_points[i + 1])
                    writer.writerow(["Side View", f"Depth {self.side_point_labels[i]} - {self.side_point_labels[i + 1]}", "", "", dist])

        print(f"Results exported to {filename}")


# Usage
tool = MeasurementTool()

# Load and process front view for width measurements
tool.load_image("C:\\coding\\man\\mannequin\\dimensiongen\\images\\frontview_goated.jpg")

# Load and process side view for depth measurements
tool.load_side_image("C:\\coding\\man\\mannequin\\dimensiongen\\images\\sideview_goated.jpg")

# After placing the points, calculate, display, and save the distances
tool.calculate_and_display_results()