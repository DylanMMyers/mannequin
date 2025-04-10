from flask import Blueprint, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
from label import calculate_measurements

main = Blueprint('main', __name__)

@main.route('/upload', methods=['POST'])
def upload_images():
    # Check if we receive all required images
    required_images = ['front1', 'front2', 'side1', 'side2']
    for img in required_images:
        if img not in request.files:
            return jsonify({"error": f"Missing {img} image"}), 400

    # Get user height from form data
    try:
        user_height_cm = float(request.form.get('height', 172))  # Default to 172cm if not provided
    except ValueError:
        return jsonify({"error": "Invalid height value"}), 400

    # Create uploads directory if it doesn't exist
    upload_dir = os.path.join(os.getcwd(), 'app', 'static', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save all images and get their paths
    image_paths = {}
    for img_name in required_images:
        img_file = request.files[img_name]
        img_path = os.path.join(upload_dir, secure_filename(img_file.filename))
        img_file.save(img_path)
        image_paths[img_name] = img_path

    try:
        # Calculate measurements using all four images
        measurements = calculate_measurements(
            image_paths['front1'],
            image_paths['front2'],
            image_paths['side1'],
            image_paths['side2'],
            user_height_cm
        )
        
        # Return measurements
        return jsonify({
            "measurements": measurements
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
