FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY src/ /app/src/
CMD ["python", "src/main.py"]