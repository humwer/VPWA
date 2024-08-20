FROM python:3.12-slim-bookworm
COPY . /app
WORKDIR /app
RUN ls /app
