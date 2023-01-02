FROM registry.gitlab.trading.ewe.info:4567/trading/build-infrastructure/ci-includes/python:3.7.3-slim

ARG GITLAB_USER
ARG GITLAB_TOKEN

RUN apt-get update && apt-get install -y --no-install-recommends git wget \
    && apt-get purge -y --auto-remove \
    && rm -rf /var/lib/apt/lists/*

COPY /requirements.txt /requirements.txt

# Install Requirements
RUN pip install --no-cache-dir -r requirements.txt

#Copy service
COPY . /service
WORKDIR /service/service

ENV PYTHONPATH "${PYTHONPATH}:/service"

RUN wget -P /service/service https://s3.amazonaws.com/rds-downloads/rds-combined-ca-bundle.pem

EXPOSE 80

CMD gunicorn --timeout 180 -w 4 -b 0.0.0.0:80 main:flask_app