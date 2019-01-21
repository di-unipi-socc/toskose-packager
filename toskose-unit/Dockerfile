# toskose-unit - base image

ARG APP_VERSION
ARG PYTHON_VERSION

ARG SUPERVISORD_VERSION
ARG SUPERVISORD_REPOSITORY=https://github.com/Supervisor/supervisor/archive/${SUPERVISORD_VERSION}.tar.gz
ARG SUPERVISORD_PATH=/toskose/supervisord

#
FROM python:${PYTHON_VERSION}-alpine as base

ENV SCRIPTS_PATH=/toskose/scripts

WORKDIR /toskose/scripts
COPY base/scripts/ .

RUN apk update > /dev/null \
    && apk add --no-cache \
    ca-certificates \
    bash \
    tree \
    && update-ca-certificates > /dev/null \
    && python -m ensurepip \
    && chmod -R +x .

#
FROM base as fetcher

ARG SUPERVISORD_REPOSITORY
ARG SUPERVISORD_VERSION
ARG SUPERVISORD_PATH

WORKDIR /toskose/scripts
RUN mkdir -p ${SUPERVISORD_PATH} \
    && ./fetcher.sh \
    ${SUPERVISORD_REPOSITORY} \
    ${SUPERVISORD_PATH} \
    && ./archiver.sh \
    ${SUPERVISORD_PATH} \
    ${SUPERVISORD_VERSION}.tar.gz \
    ${SUPERVISORD_PATH} \
    && rm ${SUPERVISORD_PATH}/${SUPERVISORD_VERSION}.tar.gz

FROM fetcher as source-tester

WORKDIR /toskose
RUN tree -a

# https://github.com/six8/pyinstaller-alpine
# Alpine uses musl instead of glibc. The PyInstaller bootloader for Linux 64
# that comes with PyInstaller is made for glibc. This Docker image builds a
# bootloader with musl.
FROM python:${PYTHON_VERSION} as installer

ARG SUPERVISORD_PATH

WORKDIR ${SUPERVISORD_PATH}
COPY --from=fetcher ${SUPERVISORD_PATH} .

RUN ls -l && \
    && pip install pyinstaller > /dev/null \
    && pyinstaller \
    --distpath ${SUPERVISORD_PATH} \
    --workpath ${SUPERVISORD_PATH}/temp \
    --noconfirm \
    --clean \
    --onefile \
    --nowindow \
    --name supervisord \
    supervisor/supervisord.py


#
# FROM base as installer
#
# WORKDIR /pyinstaller
# RUN
#
# RUN pip install pyinstaller \
#     && pyinstaller --version >&2
#
# #
# FROM base as release
# LABEL maintainer.name="Matteo Bogo" \
#       maitainer.email="matteo.bogo@gmail.com" \
#       version=$APP_VERSION
