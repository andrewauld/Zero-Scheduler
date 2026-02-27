FROM python:3.9
WORKDIR .
COPY matrix_mult.py .
RUN pip install flask
CMD ["python", "matrix_mult.py"]
LABEL authors="andrewauld"

ENTRYPOINT ["top", "-b"]