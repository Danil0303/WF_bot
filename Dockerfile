FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY templates/images /app/templates/images

WORKDIR /app

CMD ["python", "main.py"]