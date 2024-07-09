FROM python:3-alpine3.15

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=runserver.py

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
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "runserver.py"]
#CMD ["gunicorn", "-b", "0.0.0.0:7000", "-w", "4", "runserver:app"]     # This is for production deployment
