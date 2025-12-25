# COMEDK College Predictor

A web application to predict eligible engineering colleges based on COMEDK rank and branch preferences.

## Project Structure

- **backend/**: Flask application logic (`app.py`, `routes.py`, `prediction.py`).
- **frontend/**: HTML templates and static assets (CSS, JS).
- **data/**: Raw and processed datasets.
- **analysis/**: Scripts for data preprocessing and visualization.
- **docs/**: Documentation and diagrams.

## Setup Instructions

1.  **Install Dependencies**:
    `ash
    pip install -r requirements.txt
    ` 

2.  **Run the Application**:
    Navigate to the `backend` directory and run:
    `ash
    python app.py
    ` 
    The app will be available at `http://127.0.0.1:5000/`.

## Features

- **Advanced College Predictor**: 
    - Input your COMEDK rank.
    - Select **multiple preferred branches** simultaneously.
    - View eligible colleges with cutoff ranks and locations.
- **Comprehensive College List**: 
    - View separate lists for **Engineering** and **Architecture** colleges.
    - **Search functionality** to filter colleges by code, name, or location.
- **Courses & Branches Information**: 
    - Explore General Courses (MBBS, BDS, etc.).
    - View detailed lists of **Engineering** and **Architecture** branches.
    - **Search functionality** to find specific courses or codes.
- **User-Friendly Interface**: 
    - Modern, responsive design using Bootstrap 5.
    - Tabbed views for easy navigation between categories.
    - `Counselling Guidance` and `Exam Details` sections.

## Development Steps

1.  **Data Collection**: Place raw CSV data in `data/raw/`.
2.  **Preprocessing**: Run `analysis/preprocessing.py` to clean data.
3.  **Backend**: Update `prediction.py` with actual logic.
4.  **Frontend**: Enhance UI in `frontend/templates/`.
