"""
Label the file
Adjust labels for size data
Return as csv
"""

from flask import Blueprint
import cv2
import math
import mediapipe as mp
import numpy as np

main = Blueprint('main', __name__)

def landmark_distance(lm1, lm2, width, height):
    """Calculate distance between two landmarks in centimeters."""
    p1 = (int(lm1.x * width), int(lm1.y * height))
    p2 = (int(lm2.x * width), int(lm2.y * height))
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def get_scale_factor(height_cm, landmarks, width, height):
    """Calculate scale factor using multiple body segments for better accuracy."""
    # Use multiple body segments to calculate scale factor
    segments = [
        (mp.solutions.pose.PoseLandmark.NOSE, mp.solutions.pose.PoseLandmark.RIGHT_ANKLE),  # Full height
        (mp.solutions.pose.PoseLandmark.LEFT_SHOULDER, mp.solutions.pose.PoseLandmark.LEFT_ELBOW),  # Upper arm
        (mp.solutions.pose.PoseLandmark.LEFT_ELBOW, mp.solutions.pose.PoseLandmark.LEFT_WRIST),  # Lower arm
        (mp.solutions.pose.PoseLandmark.LEFT_HIP, mp.solutions.pose.PoseLandmark.LEFT_KNEE),  # Upper leg
        (mp.solutions.pose.PoseLandmark.LEFT_KNEE, mp.solutions.pose.PoseLandmark.LEFT_ANKLE),  # Lower leg
    ]
    
    scale_factors = []
    for start, end in segments:
        pixel_length = landmark_distance(landmarks[start], landmarks[end], width, height)
        
        # Known proportions of body segments relative to total height
        proportions = {
            (mp.solutions.pose.PoseLandmark.NOSE, mp.solutions.pose.PoseLandmark.RIGHT_ANKLE): 1.0,
            (mp.solutions.pose.PoseLandmark.LEFT_SHOULDER, mp.solutions.pose.PoseLandmark.LEFT_ELBOW): 0.18,
            (mp.solutions.pose.PoseLandmark.LEFT_ELBOW, mp.solutions.pose.PoseLandmark.LEFT_WRIST): 0.15,
            (mp.solutions.pose.PoseLandmark.LEFT_HIP, mp.solutions.pose.PoseLandmark.LEFT_KNEE): 0.25,
            (mp.solutions.pose.PoseLandmark.LEFT_KNEE, mp.solutions.pose.PoseLandmark.LEFT_ANKLE): 0.25
        }
        
        expected_length = height_cm * proportions[(start, end)]
        scale_factors.append(expected_length / pixel_length)
    
    # Use median scale factor to be more robust to outliers
    return np.median(scale_factors)

def calculate_measurements(front1_path, front2_path, side1_path, side2_path, user_height_cm):
    """Calculate body measurements using four standardized poses."""
    # Initialize MediaPipe Pose
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(
        static_image_mode=True,
        model_complexity=2,
        min_detection_confidence=0.5
    )
    
    # Read and process all images
    front1_image = cv2.imread(front1_path)
    front2_image = cv2.imread(front2_path)
    side1_image = cv2.imread(side1_path)
    side2_image = cv2.imread(side2_path)
    
    if any(img is None for img in [front1_image, front2_image, side1_image, side2_image]):
        raise ValueError("Could not read one or more images")
    
    # Convert BGR to RGB
    front1_rgb = cv2.cvtColor(front1_image, cv2.COLOR_BGR2RGB)
    front2_rgb = cv2.cvtColor(front2_image, cv2.COLOR_BGR2RGB)
    side1_rgb = cv2.cvtColor(side1_image, cv2.COLOR_BGR2RGB)
    side2_rgb = cv2.cvtColor(side2_image, cv2.COLOR_BGR2RGB)
    
    # Get pose landmarks for all images
    front1_results = pose.process(front1_rgb)
    front2_results = pose.process(front2_rgb)
    side1_results = pose.process(side1_rgb)
    side2_results = pose.process(side2_rgb)
    
    if not all([front1_results.pose_landmarks, front2_results.pose_landmarks, 
                side1_results.pose_landmarks, side2_results.pose_landmarks]):
        raise ValueError("Could not detect pose in one or more images")
    
    # Get landmarks and image dimensions
    front1_landmarks = front1_results.pose_landmarks.landmark
    front2_landmarks = front2_results.pose_landmarks.landmark
    side1_landmarks = side1_results.pose_landmarks.landmark
    side2_landmarks = side2_results.pose_landmarks.landmark
    
    front1_height, front1_width = front1_image.shape[:2]
    front2_height, front2_width = front2_image.shape[:2]
    side1_height, side1_width = side1_image.shape[:2]
    side2_height, side2_width = side2_image.shape[:2]
    
    # Calculate height ratio for scaling using front1 image
    measured_height = (
        landmark_distance(front1_landmarks[mp_pose.PoseLandmark.NOSE],
                        front1_landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE],
                        front1_width, front1_height)
    )
    height_ratio = user_height_cm / measured_height
    
    measurements = {}
    
    # Helper function for scaled measurements
    def scaled_distance(lm1, lm2, width, height):
        p1 = (int(lm1.x * width), int(lm1.y * height))
        p2 = (int(lm2.x * width), int(lm2.y * height))
        raw_distance = math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
        return raw_distance * height_ratio

    def calculate_circumference(width, depth):
        """Calculate circumference using elliptical approximation"""
        a = width / 2  # semi-major axis
        b = depth / 2  # semi-minor axis
        h = ((a - b) ** 2) / ((a + b) ** 2)
        return math.pi * (a + b) * (1 + (3 * h) / (10 + math.sqrt(4 - 3 * h)))
    
    # 1. Measurements from front1 (elbows, knees, feet together)
    # Elbow width
    elbow_width = scaled_distance(
        front1_landmarks[mp_pose.PoseLandmark.LEFT_ELBOW],
        front1_landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW],
        front1_width, front1_height
    ) / 2
    measurements["Arm_Circumference (est.)"] = 2 * elbow_width * math.pi
    
    # Knee width
    knee_width = 0.9 * (scaled_distance(
        front1_landmarks[mp_pose.PoseLandmark.LEFT_KNEE],
        front1_landmarks[mp_pose.PoseLandmark.RIGHT_KNEE],
        front1_width, front1_height
    )) / 2
    measurements["Leg_Circumference (est.)"] = 2 * knee_width * math.pi
    
    # Arm length (average of both sides)
    left_upper_arm = scaled_distance(
        front1_landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER],
        front1_landmarks[mp_pose.PoseLandmark.LEFT_ELBOW],
        front1_width, front1_height
    )
    left_lower_arm = scaled_distance(
        front1_landmarks[mp_pose.PoseLandmark.LEFT_ELBOW],
        front1_landmarks[mp_pose.PoseLandmark.LEFT_WRIST],
        front1_width, front1_height
    )
    right_upper_arm = scaled_distance(
        front1_landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER],
        front1_landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW],
        front1_width, front1_height
    )
    right_lower_arm = scaled_distance(
        front1_landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW],
        front1_landmarks[mp_pose.PoseLandmark.RIGHT_WRIST],
        front1_width, front1_height
    )
    measurements["Arm_Length"] = (left_upper_arm + left_lower_arm + right_upper_arm + right_lower_arm) / 2
    
    # Leg length (average across all 4 images)
    def get_leg_length(landmarks, height):
        left_leg = abs(
            (landmarks[mp_pose.PoseLandmark.LEFT_HIP].y * height) -
            (landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y * height)
        ) * height_ratio
        
        right_leg = abs(
            (landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y * height) -
            (landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].y * height)
        ) * height_ratio
        
        return (left_leg + right_leg) / 2

    # Calculate leg length from all images
    front1_leg = get_leg_length(front1_landmarks, front1_height)
    front2_leg = get_leg_length(front2_landmarks, front2_height)
    side1_leg = get_leg_length(side1_landmarks, side1_height)
    side2_leg = get_leg_length(side2_landmarks, side2_height)
    
    # Average all measurements
    measurements["Leg_Length"] = (front1_leg + front2_leg + side1_leg + side2_leg) / 4.1
    
    # 2. Measurements from front2 (wrists on hips)
    # Hip width
    hip_width = scaled_distance(
        front2_landmarks[mp_pose.PoseLandmark.LEFT_WRIST],
        front2_landmarks[mp_pose.PoseLandmark.RIGHT_WRIST],
        front2_width, front2_height
    )
    
    # 3. Measurements from side1 (chest depth)
    # Get chest depth from wrist positions
    chest_depth = abs(
        side1_landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].x * side1_width -
        side1_landmarks[mp_pose.PoseLandmark.LEFT_WRIST].x * side1_width
    ) * height_ratio
    
    # Calculate chest width (average from both front views)
    chest_width1 = scaled_distance(
        front1_landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER],
        front1_landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER],
        front1_width, front1_height
    )
    chest_width2 = scaled_distance(
        front2_landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER],
        front2_landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER],
        front2_width, front2_height
    )
    chest_width = (chest_width1 + chest_width2) / 2
    
    # Calculate chest circumference
    measurements["Chest_Circumference"] = calculate_circumference(chest_width, chest_depth)
    
    # 4. Measurements from side2 and side1 (waist depth)
    # Get waist depth as difference between back wrist in side1 and front wrist in side2
    back_point = max(
        side1_landmarks[mp_pose.PoseLandmark.LEFT_WRIST].x,
        side1_landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].x
    ) * side1_width
    
    front_point = min(
        side2_landmarks[mp_pose.PoseLandmark.LEFT_WRIST].x,
        side2_landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].x
    ) * side2_width
    
    waist_depth = abs(back_point - front_point) * height_ratio
    
    # Calculate waist width from front view (using front2 image)
    waist_width = scaled_distance(
        front2_landmarks[mp_pose.PoseLandmark.LEFT_HIP],
        front2_landmarks[mp_pose.PoseLandmark.RIGHT_HIP],
        front2_width, front2_height
    ) * 1.2  # Add 20% to account for body curvature

    # Calculate hip depth (using the back wrist position from side2)
    hip_depth = waist_depth * 1.2  # Hips typically project ~20% more than waist
    
    # Calculate final circumferences
    measurements["Waist_Circumference"] = calculate_circumference(waist_width, waist_depth)
    measurements["Hip_Circumference"] = calculate_circumference(hip_width, hip_depth)
    
    return measurements