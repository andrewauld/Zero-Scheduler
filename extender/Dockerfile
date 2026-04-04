FROM python:3.11-slim
WORKDIR /app
COPY extender/ml_extender.py .
RUN pip install flask numpy joblib prometheus-api-client scikit-learn
COPY models/gradient_boosting.pkl ./models/gradient_boosting.pkl
ENV MODEL_PATH=/app/models/gradient_boosting.pkl
ENV PROMETHEUS_URL=http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090
EXPOSE 8080
CMD ["python", "ml_extender.py"]
