FROM python:3.9-slim
WORKDIR /app
COPY pass_hash.py .
RUN pip install flask
CMD ["python", "pass_hash.py"]
LABEL authors="andrewauld"
