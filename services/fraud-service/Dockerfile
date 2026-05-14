FROM python:3.11-slim
WORKDIR /app
COPY shared/ /app/shared/
COPY services/fraud-service/ /app/services/fraud-service/
RUN pip install --no-cache-dir -r /app/services/fraud-service/requirements.txt
ENV PYTHONPATH=/app
EXPOSE 8003
CMD ["uvicorn", "services.fraud-service.src.main:app", "--host", "0.0.0.0", "--port", "8003"]
