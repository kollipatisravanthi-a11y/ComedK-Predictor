FROM python:3.11-slim

# Install system dependencies for xgboost
RUN apt-get update && apt-get install -y gcc g++ gfortran libgomp1

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["gunicorn", "run:app"]
