"""
Label the file
Adjust labels for size data
Return as csv
"""

from flask import Blueprint
import cv2
import math

main = Blueprint('main', __name__)

def calculate_measurements(front_image_path, side_image_path):
    # Load images
    front_image = cv2.imread(front_image_path)
    side_image = cv2.imread(side_image_path)
    
    # Big bad AI model goes here:
    # WIP

    # Define points (example coordinates; replace with actual logic or UI integration)
    front_points = {
        "Example point" : (101, 100)
    }

    side_points = {
        "Example point 2" : (201, 200)
    }

    # Calculate scales
    height_cm = 172  # Example height in cm; replace with user input if needed
    scale = height_cm / (front_points["Example point"][0] - front_points["Example point"][1])

    # Helper function to calculate distance in cm
    def pixel_to_cm(point1, point2, scale):
        dx = point2[0] - point1[0]
        dy = point2[1] - point1[1]
        return math.hypot(dx, dy) * scale

    # Example of reading image
    example = pixel_to_cm(front_points["Example point"], front_points["Example point"], scale)
    
    # Example of doing some calculations on the dimensions
    example_calc = example * 2

    # Return results as a dictionary
    return {
        "Example": example_calc,
        # Add other measurements here as needed
    }
