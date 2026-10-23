# Start with a lightweight Python base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and the serialized model
COPY app.py .
COPY superkart_model.joblib .

# Expose the port that the Flask app will run on
EXPOSE 7860

# Command to run the Flask application
CMD ["python", "app.py"]
