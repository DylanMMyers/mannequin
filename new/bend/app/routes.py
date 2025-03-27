from flask import Blueprint, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
from label import calculate_measurements

main = Blueprint('main', __name__)

@main.route('/upload', methods=['POST'])
def upload_images():
    # Check if we receive empty images
    if 'front_image' not in request.files or 'side_image' not in request.files:
        return jsonify({"error": "Both front and side images are required"}), 400

    # Get user height from form data
    try:
        user_height_cm = float(request.form.get('height', 172))  # Default to 172cm if not provided
    except ValueError:
        return jsonify({"error": "Invalid height value"}), 400

    front_image = request.files['front_image']
    side_image = request.files['side_image']

    # Create uploads directory if it doesn't exist
    upload_dir = os.path.join(os.getcwd(), 'app', 'static', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    
    # Set image paths
    front_image_path = os.path.join(upload_dir, secure_filename(front_image.filename))
    side_image_path = os.path.join(upload_dir, secure_filename(side_image.filename))

    # Save the images
    front_image.save(front_image_path)
    side_image.save(side_image_path)

    try:
        # Calculate measurements
        measurements = calculate_measurements(front_image_path, side_image_path, user_height_cm)
        
        # Return measurements
        return jsonify({
            "measurements": measurements
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
