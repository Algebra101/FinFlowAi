FROM python:3.11-slim
WORKDIR /app
COPY shared/ /app/shared/
COPY services/forecasting-service/ /app/services/forecasting-service/
RUN pip install --no-cache-dir fastapi uvicorn sqlalchemy python-dotenv pydantic
ENV PYTHONPATH=/app
EXPOSE 8005
CMD ["uvicorn", "services.forecasting-service.src.main:app", "--host", "0.0.0.0", "--port", "8005"]
