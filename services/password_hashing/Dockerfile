FROM python:3.9
WORKDIR .
COPY pass_hash.py .
RUN pip install flask
CMD ["python", "pass_hash.py"]
LABEL authors="andrewauld"

ENTRYPOINT ["top", "-b"]