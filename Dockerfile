FROM python:3.10-slim

WORKDIR /app

# Copy only requirements first
COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the code
COPY . /app

ENV PORT=8080

CMD ["gunicorn", "-b", ":8080", "backend:app"]
