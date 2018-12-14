ARG SUPERVISORD_VERSION=3.3.4
ARG PYTHON_VERSION=2.7-alpine
ARG ALPINE_VERSION=3.8

FROM alpine:$ALPINE_VERSION as fetcher

RUN apk update && \
    apk add ca-certificates && \
    update-ca-certificates && \
    wget https://github.com/Supervisor/supervisor/archive/3.3.4.tar.gz && \
    mkdir /source && \
    tar xf 3.3.4.tar.gz -C /source

COPY requirements.txt /source

FROM python:$PYTHON_VERSION as builder
COPY --from=fetcher /source /source
WORKDIR /source
RUN pip install -r requirements.txt && \
    easy_install supervisor

# FROM scratch as release

FROM alpine

#RUN apt-get update -y > /dev/null && \
    #apt-get install wget python python-pip -y > /dev/null && \
    #wget https://github.com/Supervisor/supervisor/archive/3.3.4.tar.gz && \
    # mkdir /source && \
    # tar xf 3.3.4.tar.gz -C /source

# WORKDIR /source/supervisor-3.3.4
# RUN pip install setuptools && \
#     python setup.py install
#
# #
# FROM python:$DOCKER_IMAGE_PYTHON_VERSION as runner
# COPY --from=builder /bin /bin/supervisor
# RUN /bin/python3 setup.py install
