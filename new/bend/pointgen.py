import cv2
import numpy as np
import math

def measure_and_save_contours(front_image_path, side_image_path, user_height_cm, output_dir="C:\coding\mannequin\old\dimensiongen\images"):
    """
    Measures body parts using contours detected from front and side images,
    and saves or displays the images with contours.

    Args:
        front_image_path (str): Path to the front view image.
        side_image_path (str): Path to the side view image.
        user_height_cm (float): User's height in centimeters for scaling.
        output_dir (str): Directory to save the output images with contours.

    Returns:
        dict: A dictionary containing measurements of body parts.
    """
    def preprocess_image(image_path):
        """Preprocess the image to extract contours."""
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, binary = cv2.threshold(blurred, 50, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        return image, binary

    def find_largest_contour(binary_image):
        """Find the largest contour in the binary image."""
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            raise ValueError("No contours found. Ensure the image has a clear body outline.")
        largest_contour = max(contours, key=cv2.contourArea)
        return largest_contour

    def calculate_distance(p1, p2):
        """Calculate Euclidean distance between two points."""
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    def calculate_measurements(contour, scale_factor):
        """Calculate key measurements from the contour."""
        # Get extreme points
        topmost = tuple(contour[contour[:, :, 1].argmin()][0])
        bottommost = tuple(contour[contour[:, :, 1].argmax()][0])
        leftmost = tuple(contour[contour[:, :, 0].argmin()][0])
        rightmost = tuple(contour[contour[:, :, 0].argmax()][0])

        # Height in pixels
        height_pixels = calculate_distance(topmost, bottommost)

        # Width at chest and waist levels
        midpoint_y = (topmost[1] + bottommost[1]) // 2
        chest_width_pixels = calculate_distance(leftmost, rightmost)

        # Convert to real-world measurements
        height_cm = height_pixels * scale_factor
        chest_circumference_cm = chest_width_pixels * scale_factor * math.pi  # Approximate as ellipse

        return {
            "Height (cm)": height_cm,
            "Chest Circumference (cm)": chest_circumference_cm,
        }

    # Process front image
    front_image, front_binary = preprocess_image(front_image_path)
    front_contour = find_largest_contour(front_binary)

    # Process side image
    side_image, side_binary = preprocess_image(side_image_path)
    side_contour = find_largest_contour(side_binary)

    # Calculate scale factor using user height and front view height in pixels
    front_height_pixels = calculate_distance(
        tuple(front_contour[front_contour[:, :, 1].argmin()][0]),
        tuple(front_contour[front_contour[:, :, 1].argmax()][0])
    )
    scale_factor = user_height_cm / front_height_pixels

    # Calculate measurements for both views
    front_measurements = calculate_measurements(front_contour, scale_factor)
    side_measurements = calculate_measurements(side_contour, scale_factor)

    # Combine results
    results = {
        "Front View Measurements": front_measurements,
        "Side View Measurements": side_measurements,
    }

    return results