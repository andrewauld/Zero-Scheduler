FROM python:3.9
WORKDIR .
COPY prime_fact.py .
RUN pip install flask
CMD ["python", "prime_fact.py"]
LABEL authors="andrewauld"

ENTRYPOINT ["top", "-b"]