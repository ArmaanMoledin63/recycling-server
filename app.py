from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from PIL import Image
import io
import tensorflow as tf
import os

app = Flask(__name__)
CORS(app)

print("Starting server...")

# Load the TFLite model
try:
    print("Attempting to load model...")
    interpreter = tf.lite.Interpreter(model_path="recycling_model.tflite")
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    print("Model loaded successfully!")
    print("Input details:", input_details)
    print("Output details:", output_details)
except Exception as e:
    print(f"Error loading model: {str(e)}")
    print("Current directory contents:", os.listdir('.'))
    interpreter = None

CATEGORIES = {
    'Cardboard': {
        'instructions': [
            'Flatten all boxes',
            'Remove tape and staples',
            'Keep dry and clean',
            'Bundle large boxes together'
        ],
        'examples': 'Boxes, packaging, shipping containers'
    },
    'Food_Waste': {
        'instructions': [
            'Remove any packaging',
            'Collect in compost bin',
            'Keep sealed to prevent odors',
            'Avoid meat and dairy if home composting'
        ],
        'examples': 'Fruit/vegetable scraps, coffee grounds, eggshells'
    },
    'Glass': {
        'instructions': [
            'Rinse thoroughly',
            'Remove caps and lids',
            'Sort by color if required',
            'Handle with care - do not break'
        ],
        'examples': 'Bottles, jars, containers'
    },
    'Metal': {
        'instructions': [
            'Clean thoroughly',
            'Remove labels if possible',
            'Crush cans to save space',
            'Separate aluminum and steel'
        ],
        'examples': 'Cans, foil, bottle caps'
    },
    'Paper': {
        'instructions': [
            'Keep clean and dry',
            'Remove plastic wrapping',
            'Stack neatly',
            'Avoid greasy or food-stained paper'
        ],
        'examples': 'Newspapers, magazines, office paper'
    },
    'Plastic': {
        'instructions': [
            'Rinse clean',
            'Check recycling number',
            'Remove caps and labels',
            'Crush to save space'
        ],
        'examples': 'Bottles, containers, packaging'
    },
    'Other': {
        'instructions': [
            'Check local guidelines',
            'Separate if multiple materials',
            'Consider reuse options',
            'When in doubt, ask recycling center'
        ],
        'examples': 'Mixed materials, uncommon items'
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
        print(f"Processing file: {file.filename}")
        
        # Process image
        image = Image.open(io.BytesIO(file.read())).convert('RGB')
        # Resize to match exactly what your model expects
        image = image.resize((299, 299), Image.LANCZOS)
        # Convert to numpy array and preprocess
        image_array = np.array(image, dtype=np.float32)
        # Normalize to [-1, 1] range instead of [0, 1]
        image_array = (image_array - 127.5) / 127.5
        image_array = np.expand_dims(image_array, axis=0)
        
        print("Image shape:", image_array.shape)
        print("Image range:", np.min(image_array), "to", np.max(image_array))

        if interpreter is None:
            print("Model not loaded, using fallback")
            category = list(CATEGORIES.keys())[0]
            confidence = 0.95
        else:
            print("Making prediction with model")
            # Set the input tensor
            interpreter.set_tensor(input_details[0]['index'], image_array)
            # Run inference
            interpreter.invoke()
            # Get predictions
            predictions = interpreter.get_tensor(output_details[0]['index'])
            
            # Print all predictions
            all_categories = list(CATEGORIES.keys())
            print("\nAll predictions:")
            for i, conf in enumerate(predictions[0]):
                print(f"{all_categories[i]}: {conf * 100:.2f}%")
            
            # Get the highest confidence prediction
            predicted_class = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_class])
            category = all_categories[predicted_class]
            print(f"\nFinal prediction: {category} with confidence: {confidence * 100:.2f}%")
        
        return jsonify({
            'success': True,
            'category': category,
            'confidence': confidence,
            'instructions': CATEGORIES[category]['instructions'],
            'examples': CATEGORIES[category]['examples']
        })
        
    except Exception as e:
        print(f"Error during prediction: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)