# FOR TESTING PURPOSE - IT DEPLOYS BOTH SUPERVISORD AND SUPERVISORCTL
# /usr/local/bin/supervisord
# /usr/local/bin/supervisorctl

#########################################
# docker image suggested by tosKeriser
#########################################
ARG TOSKERISER_RESULT=node:6

#########################################
# Generation of toskose agent logic
# (will be moved in a separated docker image)
#########################################
# FROM python:2.7-alpine as toskose-agent

# - update alpine package manager
# - add a bash (to be removed)
# - ensure pip is installed
# - install virtualenv
# RUN apk update && \
#     apk add bash && \
#     python -m ensurepip && \
#     pip install virtualenv

# - create python virtual environment
# - activate the virtual environment
# - install supervisor in virtualenv
# - TODO ? remove unecessary dependencies (check a strategy to install only supervisord
# and then removes other libs like pip, wheel, ecc..)
# - make relocatable the virtualenv (experimental feature of virtualenv, risky?)
# RUN virtualenv toskose-venv && \
#     source toskose-venv/bin/activate && \
#     pip install supervisor && \
#     virtualenv --relocatable toskose-venv && \

# TODO
# TEST STAGE to check:
# - virtualenv is installed and which version is running
# - supervisord installed into the virtual environment

#########################################

#########################################
# Solution #1 : move toskose venv using the --relocatable
# experimental feature of virtualenv (RISKY)
#########################################
# FROM $TOSKERISER_RESULT as toskosed
# COPY --from=toskose-agent /toskose-venv /toskose-venv


#########################################
# Solution #2 : install python and copy the executables
# of supervisord in a virtualenv on the image suggested by tosKeriser
# as further layers.
# may be carefull if other python interpreters already exists (conflicts?)
#########################################
ARG PYTHON_REPO=https://www.python.org/ftp/python/3.3.4/Python-3.3.4.tgz
ARG SUPERVISOR_REPO=https://github.com/Supervisor/supervisor/archive/3.3.4.tar.gz

#
FROM $TOSKERISER_RESULT as toskosed-init

ENV APP_PATH=/toskose
ENV INSTALL_DIR=/install
ENV PYTHON_REPOSITORY=$PYTHON_REPO
ENV SUPERVISOR_REPOSITORY=$SUPERVISOR_REPO

RUN mkdir -p $APP_PATH/$INSTALL_DIR
WORKDIR $APP_PATH/$INSTALL_DIR
COPY scripts/base-install.sh .

#
FROM toskosed-pre-install as toskosed-python

RUN mkdir -p $APP_PATH/$INSTALL_DIR/python
WORKDIR $APP_PATH/$INSTALL_DIR/python
COPY scripts/python-install.sh .

RUN

FROM toskosed-python as toskosed-python-test










RUN mkdir -p $APP_PATH/{python,supervisor}

WORKDIR $APP_PATH/install

COPY  ./scripts/ /scripts/
      ./config/supervisord.conf /supervisord/config/supervisord.conf

RUN chmod +x install.sh && \
    ./install.sh



FROM toskosed as testing
# TODO

FROM toskosed as release

# limitations:
# - what happen if the img fetched by toskeriser doesn't have the /bin/bash?
# for instance, the "alpine" linux img (almost all official docker images
# have an -alpine version of the same image) doesn't have the /bin/bash.
# It must be installed using "apk update && apk add bash".
# How this behaviour is managed by tosker orchestrator? because the tosca
# lifecycle operation scripts (*.sh) need to be executed using the bash.
