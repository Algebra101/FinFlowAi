FROM python:3.11-slim
WORKDIR /app
COPY shared/ /app/shared/
COPY services/banking-service/ /app/services/banking-service/
RUN pip install --no-cache-dir -r /app/services/banking-service/requirements.txt
ENV PYTHONPATH=/app
EXPOSE 8002
CMD ["uvicorn", "services.banking-service.src.main:app", "--host", "0.0.0.0", "--port", "8002"]
