from flask import Flask, request, jsonify
import tensorflow as tf
import numpy as np
from PIL import Image
import io

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Recycling Classification Server is Running!"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        file = request.files['image']
        # Convert image to RGB format
        image = Image.open(io.BytesIO(file.read())).convert('RGB')
        # Resize to match your model's input size
        image = image.resize((299, 299))  # Xception size
        
        # Convert to array and normalize
        img_array = np.array(image) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        # For now, return a dummy response
        categories = ['plastic', 'paper', 'metal', 'glass', 'organic', 'ewaste', 'others']
        return jsonify({
            'category': 'plastic',  # We'll update this with real predictions later
            'confidence': 0.95,
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run()