"""
Flask web application for COMEDK Rank Predictor.
"""

from flask import Flask, render_template, request, jsonify
from predictor import RankPredictor
import os

app = Flask(__name__)

# Initialize predictor
predictor = None

def init_predictor():
    """Initialize the predictor if model exists."""
    global predictor
    if os.path.exists('models/rank_predictor.pkl'):
        try:
            predictor = RankPredictor()
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    return False

@app.route('/')
def index():
    """Render the main page."""
    model_loaded = predictor is not None
    return render_template('index.html', model_loaded=model_loaded)

@app.route('/predict', methods=['POST'])
def predict():
    """Handle prediction requests."""
    if predictor is None:
        return jsonify({
            'error': 'Model not loaded. Please train the model first.'
        }), 500
    
    try:
        # Get scores from request
        data = request.get_json()
        physics_score = float(data.get('physics_score', 0))
        chemistry_score = float(data.get('chemistry_score', 0))
        math_score = float(data.get('math_score', 0))
        
        # Get prediction
        result = predictor.get_rank_insights(physics_score, chemistry_score, math_score)
        
        return jsonify(result)
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'model_loaded': predictor is not None
    })

if __name__ == '__main__':
    # Try to initialize predictor
    if init_predictor():
        print("Model loaded successfully!")
    else:
        print("Warning: Model not found. Please run data_generator.py and train_model.py first.")
    
    # Run the app
    # Note: Set debug=False for production deployment
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
