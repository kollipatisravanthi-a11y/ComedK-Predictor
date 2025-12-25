# COMEDK Rank Predictor 🎓

An AI-powered web application that predicts COMEDK (Consortium of Medical, Engineering and Dental Colleges of Karnataka) entrance exam ranks based on expected scores in Physics, Chemistry, and Mathematics.

## Features

- **AI-Powered Predictions**: Uses machine learning (Random Forest & Gradient Boosting) to predict ranks
- **Interactive Web Interface**: User-friendly web application built with Flask
- **Real-time Predictions**: Instant rank predictions based on subject scores
- **Performance Insights**: Detailed analysis with performance categories and recommendations
- **Confidence Intervals**: Provides rank ranges for better understanding of predictions
- **Subject-wise Analysis**: Breakdown of scores across all three subjects

## COMEDK Exam Structure

- **Physics**: 60 questions (60 marks)
- **Chemistry**: 60 questions (60 marks)
- **Mathematics**: 60 questions (60 marks)
- **Total**: 180 questions (180 marks)
- **Marking Scheme**: +1 for correct answer, 0 for incorrect (no negative marking)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/kollipatisravanthi-a11y/ComedK-Predictor.git
   cd ComedK-Predictor
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Generate training data**
   ```bash
   python data_generator.py
   ```
   This creates synthetic training data based on realistic COMEDK exam patterns.

4. **Train the model**
   ```bash
   python train_model.py
   ```
   This trains the machine learning model and saves it for predictions.

5. **Run the web application**
   ```bash
   python app.py
   ```
   The application will be available at `http://localhost:5000`

## Usage

### Web Interface

1. Open your browser and navigate to `http://localhost:5000`
2. Enter your expected scores for:
   - Physics (0-60)
   - Chemistry (0-60)
   - Mathematics (0-60)
3. Click "Predict My Rank"
4. View your predicted rank, rank range, and performance insights

### Command Line Interface

You can also use the predictor directly in Python:

```python
from predictor import RankPredictor

# Initialize predictor
predictor = RankPredictor()

# Get prediction
result = predictor.get_rank_insights(
    physics_score=55,
    chemistry_score=58,
    math_score=60
)

print(f"Predicted Rank: {result['predicted_rank']}")
print(f"Performance Category: {result['performance_category']}")
```

## Project Structure

```
ComedK-Predictor/
├── app.py                  # Flask web application
├── predictor.py            # Core prediction module
├── train_model.py          # Model training script
├── data_generator.py       # Training data generation
├── requirements.txt        # Python dependencies
├── data/                   # Training data directory
│   └── comedk_training_data.csv
├── models/                 # Trained models directory
│   ├── rank_predictor.pkl
│   └── scaler.pkl
├── templates/              # HTML templates
│   └── index.html
└── static/                 # Static files (CSS, JS)
    ├── style.css
    └── script.js
```

## Model Details

### Algorithm

The predictor uses an ensemble of machine learning models:
- **Random Forest Regressor**: Primary model with 100 estimators
- **Gradient Boosting Regressor**: Secondary model for validation

### Features

The model uses the following features for prediction:
1. Physics Score (0-60)
2. Chemistry Score (0-60)
3. Mathematics Score (0-60)
4. Total Score (0-180)

### Performance Metrics

The model achieves:
- **R² Score**: ~0.98+ (on synthetic data)
- **Mean Absolute Error**: Low prediction error
- **Root Mean Squared Error**: Minimal deviation

### Training Data

The training dataset consists of 10,000 synthetic samples that simulate realistic COMEDK exam score distributions and their corresponding ranks.

## Performance Categories

The predictor categorizes performance into five levels:

| Category | Total Score Range | Description |
|----------|------------------|-------------|
| Excellent | 150-180 | Outstanding performance, top tier |
| Very Good | 120-149 | Strong chances for good colleges |
| Good | 90-119 | Decent performance, good college options |
| Average | 60-89 | Average performance, needs improvement |
| Needs Improvement | 0-59 | More preparation required |

## API Endpoints

### POST /predict

Predicts COMEDK rank based on scores.

**Request Body:**
```json
{
  "physics_score": 55.0,
  "chemistry_score": 58.0,
  "math_score": 60.0
}
```

**Response:**
```json
{
  "predicted_rank": 1234,
  "rank_range": {
    "lower": 1111,
    "upper": 1357
  },
  "total_score": 173.0,
  "subject_scores": {
    "physics": 55.0,
    "chemistry": 58.0,
    "mathematics": 60.0
  },
  "performance_category": "Excellent",
  "message": "Outstanding performance! You're in the top tier."
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

## Technical Stack

- **Backend**: Flask (Python web framework)
- **Machine Learning**: scikit-learn
- **Data Processing**: pandas, numpy
- **Model Persistence**: joblib
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Custom CSS with gradient designs

## Limitations & Disclaimer

⚠️ **Important**: This is an AI-based prediction tool that uses synthetic training data. Actual COMEDK ranks depend on various factors including:

- Number of test takers
- Difficulty level of the exam
- Normalization procedures
- Reservation policies
- Category-specific cutoffs

The predictions provided by this tool should be used as **estimates only** and not as guaranteed outcomes.

## Future Enhancements

- [ ] Integration with real historical COMEDK data
- [ ] Category-wise rank predictions (General, OBC, SC/ST)
- [ ] College prediction based on rank
- [ ] Cutoff analysis for different colleges
- [ ] Mobile application
- [ ] Advanced analytics and visualization
- [ ] Comparison with previous years' data

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open-source and available under the MIT License.

## Contact

For questions or suggestions, please open an issue on GitHub.

---

**Note**: This tool is for educational and informational purposes only. Always refer to official COMEDK resources for accurate information about the examination and admissions process.