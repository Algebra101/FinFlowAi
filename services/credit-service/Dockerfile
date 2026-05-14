# FinCore AI — Dockerfiles for remaining services

# Credit Service
FROM python:3.11-slim
WORKDIR /app
COPY shared/ /app/shared/
COPY services/credit-service/ /app/services/credit-service/
RUN pip install --no-cache-dir fastapi uvicorn sqlalchemy python-dotenv pydantic
ENV PYTHONPATH=/app
EXPOSE 8004
CMD ["uvicorn", "services.credit-service.src.main:app", "--host", "0.0.0.0", "--port", "8004"]
