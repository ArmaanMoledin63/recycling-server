from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from PIL import Image
import io
import tensorflow as tf
import os

app = Flask(__name__)
CORS(app)

# Add confidence threshold
CONFIDENCE_THRESHOLD = 0.70  # 70% confidence threshold

print("Starting server...")
print("Current working directory:", os.getcwd())
print("Files in directory:", os.listdir())

# Load the TFLite model with more error checking
try:
    print("\nAttempting to load model...")
    model_path = "recycling_model.tflite"
    
    # Check if file exists
    if os.path.exists(model_path):
        print(f"Model file found! Size: {os.path.getsize(model_path) / (1024*1024):.2f} MB")
        interpreter = tf.lite.Interpreter(model_path=model_path)
        interpreter.allocate_tensors()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        print("Model loaded successfully!")
        print("Input details:", input_details)
        print("Output details:", output_details)
    else:
        print("Model file not found!")
        print("Current directory contents:", os.listdir())
        interpreter = None
except Exception as e:
    print(f"Error loading model: {str(e)}")
    import traceback
    traceback.print_exc()
    interpreter = None

# Categories should match your training exactly
CATEGORIES = [
    'Cardboard', 'Food_Waste', 'Glass', 'Metal', 'Paper', 'Plastic', 'Other'
]

# Instructions for each category
INSTRUCTIONS = {
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
    },
    'Uncertain': {
        'instructions': [
            'Try taking another photo with:',
            '- Better lighting',
            '- Different angle',
            '- Less background clutter',
            '- Closer to the item',
            'Or consult your local recycling guidelines'
        ],
        'examples': 'Item needs clearer image for classification'
    }
}

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "Recycling Classification Server is Running!",
        "model_loaded": interpreter is not None,
        "categories": CATEGORIES
    })

@app.route('/predict', methods=['POST'])
def predict():
    print("\nReceived prediction request")
    try:
        if interpreter is None:
            raise Exception("Model not loaded properly")

        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image file provided'
            })

        file = request.files['image']
        print(f"Processing file: {file.filename}")
        
        # Process image
        image = Image.open(io.BytesIO(file.read())).convert('RGB')
        image = image.resize((299, 299))
        image_array = np.array(image, dtype=np.float32)
        image_array = image_array / 255.0
        image_array = np.expand_dims(image_array, axis=0)
        
        print(f"Processed image shape: {image_array.shape}")
        print(f"Image value range: {image_array.min()} to {image_array.max()}")

        print("Setting tensor data...")
        interpreter.set_tensor(input_details[0]['index'], image_array)
        
        print("Running inference...")
        interpreter.invoke()
        
        print("Getting predictions...")
        predictions = interpreter.get_tensor(output_details[0]['index'])
        
        # Print all predictions
        print("\nAll predictions:")
        for i, conf in enumerate(predictions[0]):
            print(f"{CATEGORIES[i]}: {conf * 100:.2f}%")
        
        # Get top 2 predictions
        top_2_indices = np.argsort(predictions[0])[-2:][::-1]
        top_2_confidences = predictions[0][top_2_indices]
        
        # Get highest confidence prediction
        predicted_class = top_2_indices[0]
        confidence = float(top_2_confidences[0])
        category = CATEGORIES[predicted_class]
        
        print(f"\nFinal prediction: {category} with confidence: {confidence * 100:.2f}%")
        
        # If confidence is below threshold or top 2 predictions are close
        if confidence < CONFIDENCE_THRESHOLD or (top_2_confidences[0] - top_2_confidences[1]) < 0.15:
            return jsonify({
                'success': True,
                'category': 'Uncertain',
                'confidence': confidence,
                'instructions': [
                    f'This item could be either:',
                    f'1. {CATEGORIES[top_2_indices[0]]} ({(top_2_confidences[0] * 100):.1f}%)',
                    f'2. {CATEGORIES[top_2_indices[1]]} ({(top_2_confidences[1] * 100):.1f}%)',
                    '',
                    'Tips for better classification:',
                    '- Try better lighting',
                    '- Different angle',
                    '- Less background clutter',
                    '- Get closer to the item'
                ],
                'examples': 'Multiple possible categories detected'
            })
        
        return jsonify({
            'success': True,
            'category': category,
            'confidence': confidence,
            'instructions': INSTRUCTIONS[category]['instructions'],
            'examples': INSTRUCTIONS[category]['examples']
        })
        
    except Exception as e:
        print(f"Error during prediction: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)