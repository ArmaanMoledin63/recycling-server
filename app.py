from flask import Flask, request, jsonify
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
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image file provided'
            })

        file = request.files['image']
        image = Image.open(io.BytesIO(file.read())).convert('RGB')
        image = image.resize((299, 299))  # Xception size
        
        # For now, return dummy prediction
        categories = ['plastic', 'paper', 'metal', 'glass', 'organic', 'ewaste', 'others']
        
        return jsonify({
            'success': True,
            'category': 'plastic',  # Replace with actual prediction later
            'confidence': 0.95
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)