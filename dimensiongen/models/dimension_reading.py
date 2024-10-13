import cv2
import mediapipe as mp
import numpy as np
import argparse
import csv

# Initialize Mediapipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True)

# Function to calculate Euclidean distance between two points
def calculate_distance(p1, p2):
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

# Function to extract measurements using specified landmark indices
def calculate_width(landmarks, indices):
    return calculate_distance(
        (landmarks[indices[0]].x, landmarks[indices[0]].y),
        (landmarks[indices[1]].x, landmarks[indices[1]].y)
    )

def extract_measurements(front_image_path, side_image_path, arms_image_path, height_in_inches):
    # Process front image
    front_image = cv2.imread(front_image_path)
    if front_image is None:
        raise ValueError(f"Could not open or find the image: {front_image_path}")
    
    front_image_rgb = cv2.cvtColor(front_image, cv2.COLOR_BGR2RGB)
    front_results = pose.process(front_image_rgb)
    if not front_results.pose_landmarks:
        raise ValueError("Pose landmarks not detected in the front image.")
    
    # Process side image
    side_image = cv2.imread(side_image_path)
    if side_image is None:
        raise ValueError(f"Could not open or find the image: {side_image_path}")
    
    side_image_rgb = cv2.cvtColor(side_image, cv2.COLOR_BGR2RGB)
    side_results = pose.process(side_image_rgb)
    if not side_results.pose_landmarks:
        raise ValueError("Pose landmarks not detected in the side image.")

    # Process arms image
    arms_image = cv2.imread(arms_image_path)
    if arms_image is None:
        raise ValueError(f"Could not open or find the image: {arms_image_path}")

    arms_image_rgb = cv2.cvtColor(arms_image, cv2.COLOR_BGR2RGB)
    arms_results = pose.process(arms_image_rgb)
    if not arms_results.pose_landmarks:
        raise ValueError("Pose landmarks not detected in the arms image.")
    
    front_landmarks = front_results.pose_landmarks.landmark
    arms_landmarks = arms_results.pose_landmarks.landmark

    # Calculate height from front view
    height_px = calculate_distance(
        (front_landmarks[mp_pose.PoseLandmark.NOSE].x, front_landmarks[mp_pose.PoseLandmark.NOSE].y),
        (front_landmarks[mp_pose.PoseLandmark.LEFT_HEEL].x, front_landmarks[mp_pose.PoseLandmark.LEFT_HEEL].y)
    )
    
    # Scaling factor to convert from pixels to inches
    scale = height_in_inches / height_px
    
    # Torso measurements
    torso_height_px = (
        calculate_distance(
            (front_landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x, front_landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y),
            (front_landmarks[mp_pose.PoseLandmark.LEFT_HIP].x, front_landmarks[mp_pose.PoseLandmark.LEFT_HIP].y)
        ) +
        calculate_distance(
            (front_landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x, front_landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y),
            (front_landmarks[mp_pose.PoseLandmark.RIGHT_HIP].x, front_landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y)
        )
    ) / 2
    
    # Calculate shoulder width
    shoulder_width_px = calculate_distance(
        (front_landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x, front_landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y),
        (front_landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x, front_landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y)
    )

    # Calculate hip width
    hip_width_px = calculate_distance(
        (front_landmarks[mp_pose.PoseLandmark.LEFT_HIP].x, front_landmarks[mp_pose.PoseLandmark.LEFT_HIP].y),
        (front_landmarks[mp_pose.PoseLandmark.RIGHT_HIP].x, front_landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y)
    )

    # Average torso width calculation
    torso_width_px = (shoulder_width_px + hip_width_px) / 2

    torso_depth_px = torso_width_px  # Set torso depth equal to torso width

    # Arm measurements from front view
    upper_arm_length_left_px = calculate_distance(
        (front_landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x, front_landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y),
        (front_landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].x, front_landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].y)
    )
    
    lower_arm_length_left_px = calculate_distance(
        (front_landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].x, front_landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].y),
        (front_landmarks[mp_pose.PoseLandmark.LEFT_WRIST].x, front_landmarks[mp_pose.PoseLandmark.LEFT_WRIST].y)
    )
    
    upper_arm_length_right_px = calculate_distance(
        (front_landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x, front_landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y),
        (front_landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].x, front_landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].y)
    )
    
    lower_arm_length_right_px = calculate_distance(
        (front_landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].x, front_landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].y),
        (front_landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].x, front_landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].y)
    )

    # Arm measurements from arms image
    elbow_distance_px = calculate_distance(
        (arms_landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].x, arms_landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].y),
        (arms_landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].x, arms_landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].y)
    )

    # Arm widths and depths
    arm_width_px = elbow_distance_px / 4  # Adjust the factor based on preference

    upper_arm_width_left_px = arm_width_px
    upper_arm_depth_left_px = arm_width_px
    lower_arm_width_left_px = arm_width_px
    lower_arm_depth_left_px = arm_width_px
    
    upper_arm_width_right_px = arm_width_px
    upper_arm_depth_right_px = arm_width_px
    lower_arm_width_right_px = arm_width_px
    lower_arm_depth_right_px = arm_width_px

    # Leg measurements
    upper_leg_length_left_px = calculate_distance(
        (front_landmarks[mp_pose.PoseLandmark.LEFT_HIP].x, front_landmarks[mp_pose.PoseLandmark.LEFT_HIP].y),
        (front_landmarks[mp_pose.PoseLandmark.LEFT_KNEE].x, front_landmarks[mp_pose.PoseLandmark.LEFT_KNEE].y)
    )
    
    lower_leg_length_left_px = calculate_distance(
        (front_landmarks[mp_pose.PoseLandmark.LEFT_KNEE].x, front_landmarks[mp_pose.PoseLandmark.LEFT_KNEE].y),
        (front_landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].x, front_landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y)
    )
    
    upper_leg_length_right_px = calculate_distance(
        (front_landmarks[mp_pose.PoseLandmark.RIGHT_HIP].x, front_landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y),
        (front_landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].x, front_landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].y)
    )
    
    lower_leg_length_right_px = calculate_distance(
        (front_landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].x, front_landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].y),
        (front_landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].x, front_landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].y)
    )

    # Calculate lower leg width as the distance between the knees
    leg_width_px = calculate_distance(
        (front_landmarks[mp_pose.PoseLandmark.LEFT_KNEE].x, front_landmarks[mp_pose.PoseLandmark.LEFT_KNEE].y),
        (front_landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].x, front_landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].y)
    )

    # Leg depths (keeping depth consistent with width for simplicity)
    leg_depth_px = leg_width_px  # You can set a different calculation based on your requirements

    # Create measurements dictionary
    measurements = {
        "height": height_in_inches,
        "torso_height": torso_height_px * scale,
        "torso_width": torso_width_px * scale,
        "torso_depth": torso_depth_px * scale,
        "upper_arm_length_left": upper_arm_length_left_px * scale,
        "lower_arm_length_left": lower_arm_length_left_px * scale,
        "upper_arm_width_left": upper_arm_width_left_px * scale,
        "upper_arm_depth_left": upper_arm_depth_left_px * scale,
        "lower_arm_width_left": lower_arm_width_left_px * scale,
        "lower_arm_depth_left": lower_arm_depth_left_px * scale,
        "upper_arm_length_right": upper_arm_length_right_px * scale,
        "lower_arm_length_right": lower_arm_length_right_px * scale,
        "upper_arm_width_right": upper_arm_width_right_px * scale,
        "upper_arm_depth_right": upper_arm_depth_right_px * scale,
        "lower_arm_width_right": lower_arm_width_right_px * scale,
        "lower_arm_depth_right": lower_arm_depth_right_px * scale,
        "upper_leg_length_left": upper_leg_length_left_px * scale,
        "lower_leg_length_left": lower_leg_length_left_px * scale,
        "upper_leg_width_left": leg_width_px * scale,
        "upper_leg_depth_left": leg_depth_px * scale,
        "lower_leg_width_left": 0.5 * leg_width_px * scale,
        "lower_leg_depth_left": 0.5 * leg_depth_px * scale,
        "upper_leg_length_right": upper_leg_length_right_px * scale,
        "lower_leg_length_right": lower_leg_length_right_px * scale,
        "upper_leg_width_right": leg_width_px * scale,
        "upper_leg_depth_right": leg_depth_px * scale,
        "lower_leg_width_right": 0.5 * leg_width_px * scale,
        "lower_leg_depth_right": 0.5 * leg_depth_px * scale,
    }

    return measurements

# Save measurements to CSV
def save_measurements_to_csv(measurements, output_file):
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Measurement", "Value (inches)"])
        for key, value in measurements.items():
            writer.writerow([key, value])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract body measurements from images.")
    parser.add_argument("front_image", help="Path to the front view image")
    parser.add_argument("side_image", help="Path to the side view image")
    parser.add_argument("arms_image", help="Path to the arms view image")
    parser.add_argument("height", type=float, help="Height in inches")
    parser.add_argument("output", help="Output CSV file path")
    args = parser.parse_args()

    try:
        measurements = extract_measurements(args.front_image, args.side_image, args.arms_image, args.height)
        save_measurements_to_csv(measurements, args.output)
        print(f"Measurements saved to {args.output}.")
    except Exception as e:
        print(f"Error: {e}")
