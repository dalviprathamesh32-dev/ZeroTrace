FROM python:3.10-slim

WORKDIR /srv/backend

# requirements pehle: jab tak ye file nahi badlegi, pip install cache se aayega
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# code baad mein, kyunki ye roz badalta hai
COPY backend/app ./app
COPY frontend /srv/frontend

# root user se mat chala
RUN useradd -m appuser
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

