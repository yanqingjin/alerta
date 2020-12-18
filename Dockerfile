FROM python:3.8-alpine

RUN apk add --no-cache \
    bash \
    git \
    supervisor \
    build-base \
    libffi-dev \
    openssl-dev \
    postgresql-dev \
    python3-dev

COPY . /app
COPY docker-entrypoint.sh /
RUN chmod 777 /app
WORKDIR /app

RUN pip install -r requirements.txt
RUN pip install .
RUN pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=plugins/amqp
RUN pip install git+https://github.com/alerta/alerta-contrib.git#subdirectory=integrations/mailer

ENV ALERTA_SVR_CONF_FILE /app/alertad.conf
ENV ALERTA_CONF_FILE /app/alerta.conf
ENV ALERTA_ENDPOINT=http://localhost:8080

USER daemon
ENTRYPOINT ["/docker-entrypoint.sh"]

EXPOSE 8080

ENV FLASK_SKIP_DOTENV=1

CMD ["alertad", "run", "--host", "0.0.0.0", "--port", "8080"]
