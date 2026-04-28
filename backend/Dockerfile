FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app/backend

# Contexte de build = ./backend/ (Render utilise le dossier du Dockerfile)
COPY requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . /app/backend

RUN chmod +x /app/backend/entrypoint.sh

CMD ["/app/backend/entrypoint.sh"]
