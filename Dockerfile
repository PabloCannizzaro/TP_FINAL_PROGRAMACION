FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Railway sets PORT; the app reads it in solitaire/main.py
EXPOSE 8000
CMD ["python", "-m", "solitaire.main"]

