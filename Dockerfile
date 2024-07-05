FROM python:3-alpine3.15

# Install dependencies needed to build psycopg2
RUN apk update && apk add --no-cache \
    postgresql-dev \
    gcc \
    python3-dev \
    musl-dev

WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
EXPOSE 7000
CMD ["python", "runserver.py"]
