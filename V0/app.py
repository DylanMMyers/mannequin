from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time
import random
from werkzeug.utils import secure_filename
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Measurement descriptions for reference
MEASUREMENT_DESCRIPTIONS = {
    "height": "Bottom of feet to top of head",
    "chest": "Around torso - fullest part of chest, under arms",
    "underbust": "Circumference around body directly under breasts",
    "shoulders": "From outer edge of shoulder to shoulder",
    "neck": "Around middle of neck (around Adam's apple)",
    "arm_length": "Shoulder seam to wrist",
    "upper_arm": "Around thickest part of upper arm",
    "lower_arm": "Around thickest part of forearm",
    "wrist": "Around the wrist",
    "waist": "Around narrowest torso, typically above belly button",
    "low_waist": "Around waistline",
    "hips": "Around fullest part of hips/buttocks",
    "thigh": "Thickest part of upper leg",
    "knee": "Around knee cap",
    "calf": "Around thickest part of lower leg",
    "ankle": "Around fullest part of ankle",
    "inseam": "Inside leg from crotch to ankle",
    "outseam": "Outside leg from waist to ankle",
    "rise": "Front crotch seam from waist to where legs meet",
    "back_rise": "Back crotch seam from waist to where legs meet",
    "foot_length": "Heel to toe length",
    "foot_width": "Widest part of foot",
    "hand_circumference": "Around palm of hand"
}

# Mock function to analyze image and return measurements
def analyze_image(image_path):
    """
    This is a mock function that simulates image analysis.
    In a real application, this would use computer vision algorithms
    to detect body measurements from the image.
    """
    logger.info(f"Analyzing image: {image_path}")
    
    # Simulate processing time
    time.sleep(2)
    
    # Generate mock measurements with slight randomization
    # Organized by body regions
    upper_body_measurements = {
        "height": {"value": round(random.uniform(165, 190), 1), "unit": "cm", "description": MEASUREMENT_DESCRIPTIONS["height"]},
        "chest": {"value": round(random.uniform(95, 110), 1), "unit": "cm", "description": MEASUREMENT_DESCRIPTIONS["chest"]},
        "underbust": {"value": round(random.uniform(80, 95), 1), "unit": "cm", "description": MEASUREMENT_DESCRIPTIONS["underbust"]},
        "shoulders": {"value": round(random.uniform(40, 50), 1), "unit": "cm", "description": MEASUREMENT_DESCRIPTIONS["shoulders"]},
        "neck": {"value": round(random.uniform(35, 45), 1), "unit": "cm", "description": MEASUREMENT_DESCRIPTIONS["neck"]},
    }
    
    arms_measurements = {
        "arm_length": {"value": round(random.uniform(60, 70), 1), "unit": "cm", "description": MEASUREMENT_DESCRIPTIONS["arm_length"]},
        "upper_arm": {"value": round(random.uniform(25, 35), 1), "unit": "cm", "description": MEASUREMENT_DESCRIPTIONS["upper_arm"]},
        "lower_arm": {"value": round(random.uniform(20, 30), 1), "unit": "cm", "description": MEASUREMENT_DESCRIPTIONS["lower_arm"]},
        "wrist": {"value": round(random.uniform(15, 20), 1), "unit": "cm", "description": MEASUREMENT_DESCRIPTIONS["wrist"]},
    }
    
    torso_measurements = {
        "waist": {"value": round(random.uniform(75, 95), 1), "unit": "cm", "description": MEASUREMENT_DESCRIPTIONS["waist"]},
        "low_waist": {"value": round(random.uniform(80, 100), 1), "unit": "cm", "description": MEASUREMENT_DESCRIPTIONS["low_waist"]},
        "hips": {"value": round(random.uniform(95, 115), 1), "unit": "cm", "description": MEASUREMENT_DESCRIPTIONS["hips"]},
    }
    
    legs_measurements = {
        "thigh": {"value": round(random.uniform(50, 65), 1), "unit": "cm", "description": MEASUREMENT_DESCRIPTIONS["thigh"]},
        "knee": {"value": round(random.uniform(35, 45), 1), "unit": "cm", "description": MEASUREMENT_DESCRIPTIONS["knee"]},
        "calf": {"value": round(random.uniform(30, 40), 1), "unit": "cm", "description": MEASUREMENT_DESCRIPTIONS["calf"]},
        "ankle": {"value": round(random.uniform(20, 25), 1), "unit": "cm", "description": MEASUREMENT_DESCRIPTIONS["ankle"]},
        "inseam": {"value": round(random.uniform(75, 85), 1), "unit": "cm", "description": MEASUREMENT_DESCRIPTIONS["inseam"]},
        "outseam": {"value": round(random.uniform(95, 110), 1), "unit": "cm", "description": MEASUREMENT_DESCRIPTIONS["outseam"]},
    }
    
    other_measurements = {
        "rise": {"value": round(random.uniform(25, 35), 1), "unit": "cm", "description": MEASUREMENT_DESCRIPTIONS["rise"]},
        "back_rise": {"value": round(random.uniform(30, 40), 1), "unit": "cm", "description": MEASUREMENT_DESCRIPTIONS["back_rise"]},
        "foot_length": {"value": round(random.uniform(24, 30), 1), "unit": "cm", "description": MEASUREMENT_DESCRIPTIONS["foot_length"]},
        "foot_width": {"value": round(random.uniform(8, 12), 1), "unit": "cm", "description": MEASUREMENT_DESCRIPTIONS["foot_width"]},
        "hand_circumference": {"value": round(random.uniform(18, 24), 1), "unit": "cm", "description": MEASUREMENT_DESCRIPTIONS["hand_circumference"]},
    }
    
    # Combine all measurements into categories
    measurements = {
        "upperBody": upper_body_measurements,
        "arms": arms_measurements,
        "torso": torso_measurements,
        "legs": legs_measurements,
        "other": other_measurements
    }
    
    # Generate size recommendations based on measurements
    chest_value = upper_body_measurements["chest"]["value"]
    waist_value = torso_measurements["waist"]["value"]
    hip_value = torso_measurements["hips"]["value"]
    height_value = upper_body_measurements["height"]["value"]
    
    # More comprehensive size recommendation logic
    if chest_value < 90:
        tops_size = "XS"
    elif chest_value < 98:
        tops_size = "S"
    elif chest_value < 106:
        tops_size = "M"
    elif chest_value < 114:
        tops_size = "L"
    else:
        tops_size = "XL"
        
    if waist_value < 76:
        bottoms_size = "XS"
    elif waist_value < 84:
        bottoms_size = "S"
    elif waist_value < 92:
        bottoms_size = "M"
    elif waist_value < 100:
        bottoms_size = "L"
    else:
        bottoms_size = "XL"
    
    # Shoe size calculation (simplified)
    foot_length = other_measurements["foot_length"]["value"]
    eu_shoe_size = int(foot_length * 1.5)
    us_shoe_size = int((foot_length - 20) / 0.67)
    
    size_recommendations = {
        "tops": tops_size,
        "bottoms": bottoms_size,
        "dresses": tops_size if chest_value > hip_value else bottoms_size,  # More nuanced
        "shoes": f"{eu_shoe_size} EU / {us_shoe_size} US",
        "gloves": "M" if other_measurements["hand_circumference"]["value"] < 21 else "L"
    }
    
    return {
        "measurements": measurements,
        "sizeRecommendations": size_recommendations
    }

@app.route('/analyze', methods=['POST'])
def analyze():
    # Check if the post request has the file part
    if 'image' not in request.files:
        return jsonify({"error": "No image part"}), 400
    
    file = request.files['image']
    
    # If user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Process the image
        try:
            results = analyze_image(file_path)
            return jsonify(results)
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    return jsonify({"error": "File type not allowed"}), 400

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(debug=True)