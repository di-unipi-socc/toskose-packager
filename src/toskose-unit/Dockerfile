# TosKose - single unit orchestration logic

ARG APP_VERSION
ARG ALPINE_VERSION=3.8
ARG PYTHON_VERSION=2.7.15
ARG SUPERVISOR_VERSION=3.3.4

# Fetching Stage
FROM alpine:$ALPINE_VERSION as fetcher

# after the FROM instruction all the build args are reset and aren't available
# just renew them
ARG PYTHON_VERSION
ARG SUPERVISOR_VERSION

WORKDIR /data

# Setup CA for HTTPS, download and uncompress the tarballs
RUN apk update > /dev/null && \
    apk add ca-certificates > /dev/null && \
    update-ca-certificates > /dev/null && \
    mkdir -p python/ supervisor/ && \
    wget -q https://github.com/Supervisor/supervisor/archive/${SUPERVISOR_VERSION}.tar.gz \
            > /dev/null && \
    tar zxf ${SUPERVISOR_VERSION}.tar.gz -C supervisor/ --strip-components=1

# Python Base Stage
FROM python:$PYTHON_VERSION-alpine as supervisor-base
ENV APP_PATH=/supervisor

# Dependencies Stage - install dependencies
FROM supervisor-base as supervisor-dependencies
COPY dependencies/requirements.txt $APP_PATH/dependencies/requirements.txt
WORKDIR $APP_PATH/dependencies
RUN pip install -r requirements.txt

# Building Stage - install supervisor
FROM supervisor-dependencies as supervisor-builder
COPY --from=fetcher /data/supervisor $APP_PATH/source
WORKDIR $APP_PATH/source
RUN python setup.py install

# Configuration Stage - configure supervisord
FROM supervisor-builder as supervisor-configuration
WORKDIR $APP_PATH

COPY supervisor/supervisord.conf /etc/supervisord.conf
RUN rm -rf dependencies/ source/

##################################################
# Testing Stage
FROM supervisor-configuration as supervisor-testing

COPY --from=fetcher /data /test/fetcher/data

COPY tests /tests
WORKDIR /tests
RUN apk update > /dev/null && \
    apk add bash > /dev/null && \
    chmod +x integrity_test.sh supervisor_test.sh && \
    ./integrity_test.sh

# RUN echo "Testing Supervisor installation.." && \
#     echo_supervisord_conf

##################################################

# Release Stage
FROM supervisor-configuration as toskose-release
LABEL organization="di-unipi-socc" \
      developer="Matteo Bogo" \
      description="Orchestrating multiple services in a single unit of execution" \
      version=$APP_VERSION

EXPOSE 9001/tcp
ENTRYPOINT ["/usr/local/bin/supervisord", "-c", "/etc/supervisord.conf"]
