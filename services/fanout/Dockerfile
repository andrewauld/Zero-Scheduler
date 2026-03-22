FROM python:3.9-slim
WORKDIR /app
COPY fanout_func.py .
RUN pip install flask
CMD ["python", "fanout_func.py"]
LABEL authors="andrewauld"