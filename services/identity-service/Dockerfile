FROM python:3.11-slim
WORKDIR /app
COPY shared/ /app/shared/
COPY services/identity-service/ /app/services/identity-service/
RUN pip install --no-cache-dir -r /app/services/identity-service/requirements.txt
ENV PYTHONPATH=/app
EXPOSE 8006
CMD ["uvicorn", "services.identity-service.src.main:app", "--host", "0.0.0.0", "--port", "8006"]
