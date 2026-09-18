
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /worker

RUN useradd     --create-home     --uid 10001     workeruser

COPY worker.py /worker/worker.py

USER workeruser

ENTRYPOINT ["python", "/worker/worker.py"]
