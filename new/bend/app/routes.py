from flask import Blueprint, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
from label import calculate_measurements

main = Blueprint('main', __name__)

@main.route('/upload', methods=['POST'])
def upload_images():
    # check if we receive empty images (redundancy never hurt)
    if 'front_image' not in request.files or 'side_image' not in request.files:
        return jsonify({"error": "Both front and side images are required"}), 400

    front_image = request.files['front_image']
    side_image = request.files['side_image']

    # mkdir uploads to temporarily store our images
    upload_dir = os.path.join(os.getcwd(), 'app', 'static', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    
    # set image paths
    front_image_path = os.path.join(upload_dir, secure_filename(front_image.filename))
    side_image_path = os.path.join(upload_dir, secure_filename(side_image.filename))

    # save the images
    front_image.save(front_image_path)
    side_image.save(side_image_path)

    # call calculate_measurements from label.py
    measurements = calculate_measurements(front_image_path, side_image_path)

    # make the csv
    csv_path = os.path.join(upload_dir, "measurements.csv")
    import pandas as pd
    df = pd.DataFrame(list(measurements.items()), columns=["Measurement", "Value (cm)"])
    df.to_csv(csv_path, index=False)

    # download the csv to user
    return send_from_directory(upload_dir, "measurements.csv", as_attachment=True)
