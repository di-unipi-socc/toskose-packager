ARG PYTHON_VERSION=3.7.2
ARG APP_VERSION

FROM python:${PYTHON_VERSION}-slim as base
ENV TOSKOSE_MANAGER_PORT=10000
ENV TOSKOSE_APP_VERSION=APP_VERSION

WORKDIR /toskose
COPY . .

RUN apt-get update -qq \
    && apt-get install -y --no-install-recommends \
    dnsutils \
    > /dev/null \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
    && python -m ensurepip \
    && pip install -r requirements.txt \
    && chmod +x entrypoint.sh

ENTRYPOINT ["/bin/bash", "-c", "/toskose/entrypoint.sh"]
    