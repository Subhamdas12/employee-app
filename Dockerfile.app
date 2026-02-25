FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY application/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY application/ /app/application/
COPY main.py /app/main.py
COPY Employee.csv /app/Employee.csv
COPY start_worker.py /app/start_worker.py
COPY start_beat.py /app/start_beat.py
