FROM python:3.9-slim
WORKDIR /app
COPY matrix_mult.py .
RUN pip install flask numpy
CMD ["python", "matrix_mult.py"]
LABEL authors="andrewauld"