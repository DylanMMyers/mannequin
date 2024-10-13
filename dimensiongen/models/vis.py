import cv2
import mediapipe as mp

# Initialize Mediapipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Load front, side, and arms together images
front_image_path = "C:\\coding\\mannequin\\dimensiongen\\images\\frontview_goated.jpg"
side_image_path = "C:\\coding\\mannequin\\dimensiongen\\images\\sideview_goated.jpg"
arms_together_path = "C:\\coding\\mannequin\\dimensiongen\\images\\armstogether.jpg"

front_image = cv2.imread(front_image_path)
side_image = cv2.imread(side_image_path)
arms_image = cv2.imread(arms_together_path)

# Check if the images were loaded successfully
if front_image is None:
    print("Error: Could not load front image.")
    exit()
if side_image is None:
    print("Error: Could not load side image.")
    exit()
if arms_image is None:
    print("Error: Could not load arms together image.")
    exit()

# Process the front image
front_image_rgb = cv2.cvtColor(front_image, cv2.COLOR_BGR2RGB)
front_results = pose.process(front_image_rgb)

# Process the side image
side_image_rgb = cv2.cvtColor(side_image, cv2.COLOR_BGR2RGB)
side_results = pose.process(side_image_rgb)

# Process the arms together image
arms_image_rgb = cv2.cvtColor(arms_image, cv2.COLOR_BGR2RGB)
arms_results = pose.process(arms_image_rgb)

# Visualization code
mp_drawing = mp.solutions.drawing_utils

# Draw landmarks on the front image
mp_drawing.draw_landmarks(front_image, front_results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

# Draw landmarks on the side image
mp_drawing.draw_landmarks(side_image, side_results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

# Draw landmarks on the arms together image
mp_drawing.draw_landmarks(arms_image, arms_results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

# Resize images for better visibility
height_front, width_front = front_image.shape[:2]
new_height_front = int(height_front * 0.5)  # Resize to 50% of original height
new_width_front = int(width_front * 0.5)     # Resize to 50% of original width
resized_front_image = cv2.resize(front_image, (new_width_front, new_height_front))

height_side, width_side = side_image.shape[:2]
new_height_side = int(height_side * 0.5)  # Resize to 50% of original height
new_width_side = int(width_side * 0.5)     # Resize to 50% of original width
resized_side_image = cv2.resize(side_image, (new_width_side, new_height_side))

height_arms, width_arms = arms_image.shape[:2]
new_height_arms = int(height_arms * 0.5)  # Resize to 50% of original height
new_width_arms = int(width_arms * 0.5)     # Resize to 50% of original width
resized_arms_image = cv2.resize(arms_image, (new_width_arms, new_height_arms))

# Create resizable windows and show images
cv2.namedWindow('Front View with Landmarks', cv2.WINDOW_NORMAL)
cv2.imshow('Front View with Landmarks', resized_front_image)

cv2.namedWindow('Side View with Landmarks', cv2.WINDOW_NORMAL)
cv2.imshow('Side View with Landmarks', resized_side_image)

cv2.namedWindow('Arms Together View with Landmarks', cv2.WINDOW_NORMAL)
cv2.imshow('Arms Together View with Landmarks', resized_arms_image)

cv2.waitKey(0)
cv2.destroyAllWindows()
