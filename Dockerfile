FROM python:3.12-alpine

WORKDIR /app

COPY . /app

RUN chmod -R 755 /app

ENV PORT=8080
EXPOSE 8080

CMD ["python", "server.py"]
