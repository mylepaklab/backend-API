FROM python:3.10-slim

WORKDIR /app

# Copy only requirements first for better Docker caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "\
from sentence_transformers import SentenceTransformer; \
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')"

# Now copy the rest of the app
COPY . /app

# Set the environment port (used by Gunicorn)
ENV PORT=8080

# Run the app with Gunicorn (longer timeout to prevent SIGKILL on slow load)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--timeout", "120", "backend:app"]

