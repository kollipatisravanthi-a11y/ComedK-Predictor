# COMEDK College Predictor & Chatbot Assistant 🎓

A comprehensive web application designed to help students navigate the COMEDK UGET counseling process. It features a Machine Learning-based college predictor, an AI chatbot for instant result, and detailed information about colleges and courses.

## 🚀 Key Features

*   **🏆 Advanced College Predictor**: Uses historical data (2021-2025) and Trend Analysis to predict eligible engineering colleges and branches based on your 2026 rank.
*   **🤖 AI Chatbot Assistant**: A Natural Language Processing (NLP) powered assistant capable of answering queries about Syllabus, Cutoffs (General/HK), Exam Patterns, and College info.
*   **📚 Course Explorer**: Detailed insights into available Engineering, Medical, and Architecture courses.
*   **🏛️ College Directory**: Searchable list of Top Engineering colleges in Karnataka with location and code details.
*   **📈 Historical Data Analysis**: Built on verified cutoff data from the last 5 years.

## 🛠️ Tech Stack

*   **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5 (Responsive Design)
*   **Backend**: Python, Flask
*   **Machine Learning / AI**: 
    *   `scikit-learn` for Rank Prediction (Linear Regression & Trend Analysis).
    *   NLP (Bag of Words) for the Chatbot.
*   **Data Processing**: Pandas, NumPy.
*   **Database**: JSON/CSV file storage for rapid access.

## 📂 Project Structure

```
COMEDK_DTL/
├── backend/
│   ├── app.py                # Main Flask Application Factory
│   ├── routes.py            # URL Routing & Controller Logic
│   ├── store_predictions.py # Prediction Engine (Generates 2026 forecasts)
│   ├── chatbot_ai.py        # NLP Chatbot Implementation
│   ├── intents.json         # Chatbot Training Data
│   └── colleges_data.py     # Data Access Layer
├── data/
│   └── processed/           # Cleaned datasets
├── frontend/
│   ├── static/              # CSS, Images, JS
│   └── templates/           # HTML Templates (Jinja2)
├── COMEDK_MASTER_2021_2025.csv  # Primary Historical Dataset
└── run.py                   # Application Entry Point
```

## ☁️ Deployment

### Use Railway or Heroku (Alternatives)

This project is now configured with a standard `Procfile`, which makes it compatible with most Platform-as-a-Service (PaaS) providers like **Railway**, **Heroku**, or **Fly.io**.

#### Deploy on Railway (Recommended)

1.  Sign up at [railway.app](https://railway.app/).
2.  Click "New Project" -> "Deploy from GitHub repo".
3.  Select your repository `ComedK-Predictor`.
4.  Railway will automatically detect the `Procfile` and deploy your app.
    *   *Note: Accessing the `comedk.db` works because the Procfile command rebuilds it every time the server starts (`python setup_db.py`).*

#### Deploy on Heroku

1.  Install the Heroku CLI and login (`heroku login`).
2.  Create a new app: `heroku create`.
3.  Deploy: `git push heroku main`.

## ⚙️ Installation & Setup

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/kollipatisravanthi-a11y/ComedK-Predictor.git
    cd COMEDK_DTL
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Initialize Database**:
    This step creates the `comedk.db` file from the CSV data.
    ```bash
    python setup_db.py
    ```

4.  **Run the Application**:
    ```bash
    python run.py
    ```
    Access the app at `http://127.0.0.1:5000`

2.  **Create a Virtual Environment (Optional but Recommended)**:
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Application**:
    ```bash
    python run.py
    ```
    The application will start at `http://127.0.0.1:5000/`

## 👥 Meet the Team

*   **Kollipati Lakshmi Sravanthi** - Project Lead
*   **K Manoj Kumar** - Backend Developer
*   **Nanda Kumar HR** - Frontend Developer
*   **NR Mahesh Raju** - Database Admin

---
*© 2025-2026 COMEDK Predictor. All Rights Reserved.*
