FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "echo '=== DJANGO STARTING ===' && echo \"PORT=$PORT\" && echo \"DATABASE_HOST=$DATABASE_HOST\" && echo \"DATABASE_NAME=$DATABASE_NAME\" && echo \"DATABASE_USER=$DATABASE_USER\" && echo \"DATABASE_PORT=$DATABASE_PORT\" && python manage.py check && echo '=== CHECK PASSED ===' && python manage.py migrate && echo '=== MIGRATION PASSED ===' && exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT}"]