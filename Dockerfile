FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "echo '=== DJANGO STARTING ===' && echo \"PORT=$PORT\" && echo \"HOST=$DATABASE_HOST\" && python manage.py check && echo '=== CHECK PASSED ===' && python manage.py runserver 0.0.0.0:$PORT"]