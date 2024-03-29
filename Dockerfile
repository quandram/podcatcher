FROM python:3

COPY requirements.txt /requirements.txt
RUN pip install -r requirements.txt

VOLUME ["/code", "/pods"]

CMD ["python", "/code/feed-runner.py"]