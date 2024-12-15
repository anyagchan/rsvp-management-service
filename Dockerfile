FROM python:3.9

WORKDIR /app

# Copy requirements.txt first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code to the working directory
COPY ./app ./app

# Command to run the FastAPI app using uvicorn from within the app folder
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]