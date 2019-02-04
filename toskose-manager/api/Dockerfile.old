#

ARG APP_VERSION
ARG PYTHON_VERSION=2.7.15
ARG SUPERVISORD_VERSION=3.3.5

FROM python:${PYTHON_VERSION}-alpine as base

RUN apk update --quiet \
    && apk add --no-cache --quiet \
    ca-certificates \
    && update-ca-certificates > /dev/null \
    && rm -rf /var/cache/apk/*

FROM base as release

WORKDIR /toskose
COPY resources/requirements.txt ./src ./

RUN python -m ensurepip \
    && pip install --quiet \
    -r requirements.txt

EXPOSE 9002/tcp

ENTRYPOINT ["gunicorn","--bind","0.0.0.0:9002","entrypoint:app"]
