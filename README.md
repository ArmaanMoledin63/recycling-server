# Recycling Classification Server

A Flask-based server that uses a TensorFlow Lite model to classify images of recyclable items into different categories. The server provides recycling instructions and examples for each category.

## Features

- Image classification for 7 recycling categories:
  - Cardboard
  - Food Waste
  - Glass
  - Metal
  - Paper
  - Plastic
  - Other

- Real-time classification with confidence scores
- Detailed recycling instructions for each category
- Automatic uncertainty handling for low-confidence predictions
- CORS support for cross-origin requests
- Built with TensorFlow Lite for efficient inference

## Requirements

- Python 3.8+
- TensorFlow Lite model file (`recycling_model.tflite`)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd recycling-server
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Ensure the TensorFlow Lite model file (`recycling_model.tflite`) is in the root directory.

## Project Structure

```
recycling-server/
├── app.py                 # Main server application
├── recycling_model.tflite # TFLite model file
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## API Endpoints

### GET /
Health check endpoint that returns server status and available categories.

Response:
```json
{
    "status": "Recycling Classification Server is Running!",
    "model_loaded": true,
    "categories": ["Cardboard", "Food_Waste", "Glass", "Metal", "Paper", "Plastic", "Other"]
}
```

### POST /predict
Endpoint for image classification.

Request:
- Method: POST
- Content-Type: multipart/form-data
- Body: image file (field name: "image")

Response:
```json
{
    "success": true,
    "category": "Plastic",
    "confidence": 0.95,
    "instructions": [
        "Rinse clean",
        "Check recycling number",
        "Remove caps and labels",
        "Crush to save space"
    ],
    "examples": "Bottles, containers, packaging"
}
```

## Configuration

The server includes several configurable parameters:

- `CONFIDENCE_THRESHOLD`: Minimum confidence level for predictions (default: 0.70)
- `CATEGORIES`: List of classification categories
- `INSTRUCTIONS`: Dictionary of recycling instructions and examples for each category

## Running the Server

### Development
```bash
python app.py
```
The server will start on `http://localhost:5000`

### Production
```bash
gunicorn app:app
```

## Error Handling

The server includes comprehensive error handling:
- Image processing errors
- Model loading failures
- Invalid requests
- Low confidence predictions

For uncertain classifications (confidence < 70% or close predictions), the server returns detailed feedback and improvement suggestions.

## Model Information

The server uses an Xception-based TensorFlow Lite model optimized for recycling classification. The model:
- Accepts 299x299 RGB images
- Provides confidence scores for 7 categories
- Is optimized for mobile and edge deployment

## Security Notes

- The server includes CORS support for cross-origin requests
- Input validation is implemented for file uploads
- Error messages are sanitized for production use

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]
