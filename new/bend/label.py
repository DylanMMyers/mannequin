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

def calculate_measurements(front_image_path, side_image_path, user_height_cm):
    """Calculate body measurements using standardized poses."""
    # Initialize MediaPipe Pose
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(
        static_image_mode=True,
        model_complexity=2,
        min_detection_confidence=0.5
    )
    
    # Read and process images
    front_image = cv2.imread(front_image_path)
    side_image = cv2.imread(side_image_path)
    
    if front_image is None or side_image is None:
        raise ValueError("Could not read one or both images")
    
    # Convert BGR to RGB
    front_rgb = cv2.cvtColor(front_image, cv2.COLOR_BGR2RGB)
    side_rgb = cv2.cvtColor(side_image, cv2.COLOR_BGR2RGB)
    
    # Get pose landmarks
    front_results = pose.process(front_rgb)
    side_results = pose.process(side_rgb)
    
    if not front_results.pose_landmarks or not side_results.pose_landmarks:
        raise ValueError("Could not detect pose in one or both images")
    
    front_landmarks = front_results.pose_landmarks.landmark
    side_landmarks = side_results.pose_landmarks.landmark
    front_height, front_width = front_image.shape[:2]
    side_height, side_width = side_image.shape[:2]
    
    # Calculate measured height using multiple segments
    measured_height = (
        landmark_distance(front_landmarks[mp_pose.PoseLandmark.NOSE],
                        front_landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER],
                        front_width, front_height) +
        landmark_distance(front_landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER],
                        front_landmarks[mp_pose.PoseLandmark.RIGHT_HIP],
                        front_width, front_height) +
        landmark_distance(front_landmarks[mp_pose.PoseLandmark.RIGHT_HIP],
                        front_landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE],
                        front_width, front_height)
    )
    
    # Calculate height ratio for scaling
    height_ratio = user_height_cm / measured_height
    
    # Helper function for scaled measurements
    def scaled_distance(lm1, lm2, width, height):
        p1 = (int(lm1.x * width), int(lm1.y * height))
        p2 = (int(lm2.x * width), int(lm2.y * height))
        raw_distance = math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
        return raw_distance * height_ratio
    
    measurements = {}
    
    # Height (already scaled by definition)
    measurements["Height"] = user_height_cm
    
    # Calculate arm length from both views using upper and lower arm segments
    front_upper_arm = (
        landmark_distance(front_landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER],
                        front_landmarks[mp_pose.PoseLandmark.LEFT_ELBOW],
                        front_width, front_height) +
        landmark_distance(front_landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER],
                        front_landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW],
                        front_width, front_height)
    ) / 2

    front_lower_arm = (
        landmark_distance(front_landmarks[mp_pose.PoseLandmark.LEFT_ELBOW],
                        front_landmarks[mp_pose.PoseLandmark.LEFT_WRIST],
                        front_width, front_height) +
        landmark_distance(front_landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW],
                        front_landmarks[mp_pose.PoseLandmark.RIGHT_WRIST],
                        front_width, front_height)
    ) / 2

    side_upper_arm = landmark_distance(
        side_landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER],
        side_landmarks[mp_pose.PoseLandmark.LEFT_ELBOW],
        side_width, side_height
    )

    side_lower_arm = landmark_distance(
        side_landmarks[mp_pose.PoseLandmark.LEFT_ELBOW],
        side_landmarks[mp_pose.PoseLandmark.LEFT_WRIST],
        side_width, side_height
    )

    # Average both views and sum upper and lower arm segments
    front_total_arm = (front_upper_arm + front_lower_arm) * height_ratio
    side_total_arm = (side_upper_arm + side_lower_arm) * height_ratio
    measurements["Arm_Length"] = (front_total_arm + side_total_arm) / 2
    
    # Calculate leg length from both views
    front_leg_length = (
        landmark_distance(front_landmarks[mp_pose.PoseLandmark.LEFT_HIP],
                        front_landmarks[mp_pose.PoseLandmark.LEFT_ANKLE],
                        front_width, front_height) +
        landmark_distance(front_landmarks[mp_pose.PoseLandmark.RIGHT_HIP],
                        front_landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE],
                        front_width, front_height)
    ) / 2

    side_leg_length = landmark_distance(
        side_landmarks[mp_pose.PoseLandmark.LEFT_HIP],
        side_landmarks[mp_pose.PoseLandmark.LEFT_ANKLE],
        side_width, side_height
    )

    # Average both views for leg length
    measurements["Leg_Length"] = (front_leg_length + side_leg_length) / 2 * height_ratio
    
    # Calculate knee width using knees pressed together
    knee_width = scaled_distance(
        front_landmarks[mp_pose.PoseLandmark.LEFT_KNEE],
        front_landmarks[mp_pose.PoseLandmark.RIGHT_KNEE],
        front_width, front_height
    )
    measurements["Knee_Width"] = knee_width
    
    # Calculate elbow width using elbows pressed together
    elbow_width = scaled_distance(
        front_landmarks[mp_pose.PoseLandmark.LEFT_ELBOW],
        front_landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW],
        front_width, front_height
    ) * 1.75  # Multiply by 1.75 to get more accurate measurement
    measurements["Elbow_Width"] = elbow_width
    
    # Calculate chest using shoulder width and depth
    shoulder_width = scaled_distance(
        front_landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER],
        front_landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER],
        front_width, front_height
    )
    chest_depth = scaled_distance(
        side_landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER],
        side_landmarks[mp_pose.PoseLandmark.LEFT_HIP],
        side_width, side_height
    ) * 0.6  # Chest depth is typically 60% of shoulder-to-hip depth
    measurements["Chest"] = (shoulder_width * 0.85 + chest_depth) * math.pi / 2
    
    return measurements
