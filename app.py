from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from PIL import Image
import io

app = Flask(__name__)
CORS(app)

# Categories and their recycling instructions
CATEGORIES = {
    'plastic': {
        'instructions': [
            'Rinse container thoroughly',
            'Remove caps and labels',
            'Check for recycling number (1-7)',
            'Crush if possible to save space'
        ],
        'examples': 'Bottles, containers, packaging'
    },
    'paper': {
        'instructions': [
            'Keep dry and clean',
            'Remove any plastic wrapping',
            'Flatten boxes',
            'Remove any tape or staples'
        ],
        'examples': 'Newspapers, cardboard, magazines'
    },
    'metal': {
        'instructions': [
            'Clean the item thoroughly',
            'Remove any non-metal parts',
            'Crush cans to save space',
            'Check if item is magnetic (steel) or not (aluminum)'
        ],
        'examples': 'Cans, foil, bottle caps'
    },
    'glass': {
        'instructions': [
            'Rinse thoroughly',
            'Remove caps and lids',
            'Separate by color if required',
            'Do not break intentionally'
        ],
        'examples': 'Bottles, jars, containers'
    },
    'organic': {
        'instructions': [
            'Remove any packaging',
            'Cut large items into smaller pieces',
            'Keep separate from non-organic waste',
            'Compost if possible'
        ],
        'examples': 'Food waste, garden waste, wood'
    },
    'ewaste': {
        'instructions': [
            'Remove batteries if possible',
            'Keep intact - do not break',
            'Store in dry place',
            'Take to designated e-waste center'
        ],
        'examples': 'Electronics, batteries, cables'
    },
    'others': {
        'instructions': [
            'Check local recycling guidelines',
            'Consider if item can be reused',
            'Separate different materials if possible',
            'When in doubt, ask recycling center'
        ],
        'examples': 'Mixed materials, unknown items'
    }
}

@app.route('/', methods=['GET'])
def home():
    return "Recycling Classification Server is Running!"

@app.route('/predict', methods=['POST'])
def predict():
    print("Received prediction request")
    try:
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image file provided'
            })

        file = request.files['image']
        print(f"Received file: {file.filename}")
        
        # For now, return test prediction (later will connect to your model)
        category = 'plastic'  # This will be replaced with actual model prediction
        return jsonify({
            'success': True,
            'category': category,
            'confidence': 0.95,
            'instructions': CATEGORIES[category]['instructions'],
            'examples': CATEGORIES[category]['examples']
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)