FROM python:3.11-slim

WORKDIR /app

# Copy shared modules first (for caching)
COPY shared/ /app/shared/

# Copy service
COPY services/payment-service/ /app/services/payment-service/

# Install dependencies
RUN pip install --no-cache-dir -r /app/services/payment-service/requirements.txt

# Set Python path so shared modules are importable
ENV PYTHONPATH=/app

EXPOSE 8001

CMD ["uvicorn", "services.payment-service.src.main:app", "--host", "0.0.0.0", "--port", "8001"]
