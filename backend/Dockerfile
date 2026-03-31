FROM python:3.11-slim

WORKDIR /code

# Install system dependencies including those needed for psycopg2 (if used)
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy application source
COPY ./app /code/app

# Run the FastAPI app with Uvicorn
CMD ["fastapi", "run", "app/main.py", "--port", "8000"]
