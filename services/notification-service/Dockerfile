FROM python:3.11-slim
WORKDIR /app
COPY shared/ /app/shared/
COPY services/notification-service/ /app/services/notification-service/
RUN pip install --no-cache-dir fastapi uvicorn python-dotenv pydantic
ENV PYTHONPATH=/app
EXPOSE 8007
CMD ["uvicorn", "services.notification-service.src.main:app", "--host", "0.0.0.0", "--port", "8007"]
