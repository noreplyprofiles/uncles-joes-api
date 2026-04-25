FROM python:3.9-slim

WORKDIR /app
COPY . .

RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-dev

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
