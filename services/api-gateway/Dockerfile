FROM python:3.11-slim
WORKDIR /app
COPY shared/ /app/shared/
COPY services/api-gateway/ /app/services/api-gateway/
RUN pip install --no-cache-dir -r /app/services/api-gateway/requirements.txt
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn", "services.api-gateway.src.main:app", "--host", "0.0.0.0", "--port", "8000"]
