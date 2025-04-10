import cv2
import numpy as np
import math
import os

def measure_and_save_contours(front_image_path, side_image_path, user_height_cm, output_dir="C:\coding\mannequin\old\dimensiongen\images"):
    """
    Measures body parts using pose estimation from front and side images.
    Uses OpenCV's DNN module with a pre-trained pose estimation model.

    Args:
        front_image_path (str): Path to the front view image.
        side_image_path (str): Path to the side view image.
        user_height_cm (float): User's height in centimeters for scaling.
        output_dir (str): Directory to save the output images with keypoints.

    Returns:
        dict: A dictionary containing measurements of body parts.
    """
    def load_pose_model():
        """Load the OpenPose model."""
        # Get the directory containing this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        models_dir = os.path.join(current_dir, "models")
        
        # Construct paths to model files
        prototxt_path = os.path.join(models_dir, "pose_deploy_linevec.prototxt")
        caffemodel_path = os.path.join(models_dir, "pose_iter_440000.caffemodel")
        
        # Check if model files exist
        if not os.path.exists(prototxt_path) or not os.path.exists(caffemodel_path):
            raise FileNotFoundError(
                "Model files not found. Please run download_models.py first to download the required files."
            )
        
        # Load the pre-trained model
        net = cv2.dnn.readNetFromCaffe(prototxt_path, caffemodel_path)
        return net

    def preprocess_image(image_path):
        """Preprocess the image for pose estimation."""
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Get image dimensions
        height, width = image.shape[:2]
        
        # Prepare the image for the network
        blob = cv2.dnn.blobFromImage(
            image,
            1.0 / 255,
            (368, 368),
            (0, 0, 0),
            swapRB=False,
            crop=False
        )
        
        return image, blob, (width, height)

    def get_keypoints(net, blob, image_shape):
        """Get body keypoints using pose estimation."""
        # Forward pass through the network
        net.setInput(blob)
        output = net.forward()
        
        # Get the keypoints
        keypoints = []
        for i in range(output.shape[1]):
            heatMap = output[0, i, :, :]
            _, conf, _, point = cv2.minMaxLoc(heatMap)
            x = (point[0] * image_shape[0]) / output.shape[3]
            y = (point[1] * image_shape[1]) / output.shape[2]
            keypoints.append((int(x), int(y)))
        
        return keypoints

    def calculate_distance(p1, p2):
        """Calculate Euclidean distance between two points."""
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    def calculate_circumference(p1, p2, p3, scale_factor):
        """Calculate circumference using three points (approximate as ellipse)."""
        width = calculate_distance(p1, p2) * scale_factor
        depth = calculate_distance(p2, p3) * scale_factor
        return math.pi * (width + depth) / 2

    def calculate_measurements(front_keypoints, side_keypoints, scale_factor):
        """Calculate all body measurements from keypoints."""
        # Define keypoint indices for different body parts
        # These indices correspond to OpenPose's keypoint mapping
        measurements = {}
        
        # Height (from top of head to bottom of feet)
        if front_keypoints[0] and front_keypoints[15]:  # Nose to Right ankle
            measurements["Height"] = calculate_distance(front_keypoints[0], front_keypoints[15]) * scale_factor
        
        # Chest circumference (using shoulders and chest points)
        if front_keypoints[2] and front_keypoints[5] and front_keypoints[1]:  # Shoulders and chest
            measurements["Chest"] = calculate_circumference(
                front_keypoints[2], front_keypoints[5], front_keypoints[1], scale_factor
            )
        
        # Shoulder width
        if front_keypoints[2] and front_keypoints[5]:  # Left and right shoulders
            measurements["Shoulders"] = calculate_distance(front_keypoints[2], front_keypoints[5]) * scale_factor
        
        # Neck circumference
        if front_keypoints[17] and front_keypoints[18]:  # Neck points
            measurements["Neck"] = calculate_circumference(
                front_keypoints[17], front_keypoints[18], front_keypoints[1], scale_factor
            )
        
        # Arm length
        if front_keypoints[2] and front_keypoints[4]:  # Shoulder to elbow
            measurements["Arm"] = calculate_distance(front_keypoints[2], front_keypoints[4]) * scale_factor
        
        # Upper arm circumference
        if front_keypoints[2] and front_keypoints[3] and front_keypoints[4]:  # Upper arm points
            measurements["Upper_Arm"] = calculate_circumference(
                front_keypoints[2], front_keypoints[3], front_keypoints[4], scale_factor
            )
        
        # Lower arm circumference
        if front_keypoints[3] and front_keypoints[4] and front_keypoints[7]:  # Lower arm points
            measurements["Lower_Arm"] = calculate_circumference(
                front_keypoints[3], front_keypoints[4], front_keypoints[7], scale_factor
            )
        
        # Wrist circumference
        if front_keypoints[4] and front_keypoints[7]:  # Wrist points
            measurements["Wrist"] = calculate_circumference(
                front_keypoints[4], front_keypoints[7], front_keypoints[6], scale_factor
            )
        
        # Waist circumference
        if front_keypoints[8] and front_keypoints[11] and front_keypoints[1]:  # Waist points
            measurements["Waist"] = calculate_circumference(
                front_keypoints[8], front_keypoints[11], front_keypoints[1], scale_factor
            )
        
        # Hip circumference
        if front_keypoints[8] and front_keypoints[11] and front_keypoints[12]:  # Hip points
            measurements["Hip"] = calculate_circumference(
                front_keypoints[8], front_keypoints[11], front_keypoints[12], scale_factor
            )
        
        # Thigh circumference
        if front_keypoints[9] and front_keypoints[12] and front_keypoints[13]:  # Thigh points
            measurements["Thigh"] = calculate_circumference(
                front_keypoints[9], front_keypoints[12], front_keypoints[13], scale_factor
            )
        
        # Knee circumference
        if front_keypoints[13] and front_keypoints[14] and front_keypoints[10]:  # Knee points
            measurements["Knee"] = calculate_circumference(
                front_keypoints[13], front_keypoints[14], front_keypoints[10], scale_factor
            )
        
        # Calf circumference
        if front_keypoints[14] and front_keypoints[15] and front_keypoints[16]:  # Calf points
            measurements["Calf"] = calculate_circumference(
                front_keypoints[14], front_keypoints[15], front_keypoints[16], scale_factor
            )
        
        # Ankle circumference
        if front_keypoints[15] and front_keypoints[16]:  # Ankle points
            measurements["Ankle"] = calculate_circumference(
                front_keypoints[15], front_keypoints[16], front_keypoints[14], scale_factor
            )
        
        # Inseam (from crotch to ankle)
        if front_keypoints[8] and front_keypoints[15]:  # Crotch to ankle
            measurements["Inseam"] = calculate_distance(front_keypoints[8], front_keypoints[15]) * scale_factor
        
        # Outseam (from waist to ankle)
        if front_keypoints[11] and front_keypoints[15]:  # Waist to ankle
            measurements["Outseam"] = calculate_distance(front_keypoints[11], front_keypoints[15]) * scale_factor
        
        # Rise (from crotch to waist)
        if front_keypoints[8] and front_keypoints[11]:  # Crotch to waist
            measurements["Rise"] = calculate_distance(front_keypoints[8], front_keypoints[11]) * scale_factor
        
        # Foot measurements from side view
        if side_keypoints[15] and side_keypoints[16]:  # Foot points
            measurements["Foot_Length"] = calculate_distance(side_keypoints[15], side_keypoints[16]) * scale_factor
            measurements["Foot_Width"] = calculate_distance(side_keypoints[15], side_keypoints[16]) * scale_factor * 0.3
        
        # Hand circumference
        if front_keypoints[4] and front_keypoints[7]:  # Hand points
            measurements["Hand_Circumference"] = calculate_circumference(
                front_keypoints[4], front_keypoints[7], front_keypoints[6], scale_factor
            )
        
        return measurements

    # Load the pose estimation model
    net = load_pose_model()

    # Process front image
    front_image, front_blob, front_shape = preprocess_image(front_image_path)
    front_keypoints = get_keypoints(net, front_blob, front_shape)

    # Process side image
    side_image, side_blob, side_shape = preprocess_image(side_image_path)
    side_keypoints = get_keypoints(net, side_blob, side_shape)

    # Calculate scale factor using user height and front view height in pixels
    if front_keypoints[0] and front_keypoints[15]:  # Nose to Right ankle
        front_height_pixels = calculate_distance(front_keypoints[0], front_keypoints[15])
        scale_factor = user_height_cm / front_height_pixels
    else:
        raise ValueError("Could not detect height points in the image")

    # Calculate measurements using keypoints
    measurements = calculate_measurements(front_keypoints, side_keypoints, scale_factor)

    return measurements