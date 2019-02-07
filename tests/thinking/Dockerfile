# the image to be "toskosed"
ARG TOSCA_NODES_CONTAINER_IMAGE
ARG TOSCA_NODES_SOFTWARE_APPS_NAMES
ARG TOSCA_NODES_SOFTWARE_STUFF_PATH

# "toskose" an given image
FROM ${TOSCA_NODES_CONTAINER_IMAGE} as toskosed
ARG TOSCA_NODES_SOFTWARE_APPS_NAMES
ARG TOSCA_NODES_SOFTWARE_STUFF_PATH

# copy the toskose-unit's supervisord bundle (supervisord + python 2.7.15)
WORKDIR /
# check: copy from remote image (no need to declare toskose_unit as an empty from)
COPY --from=diunipisocc/toskose-unit:latest /toskose/ /toskose/

# copy lifecyle scripts and artifacts of apps hosted by this image
COPY ${TOSCA_NODES_SOFTWARE_STUFF_PATH} /tmp/toskose/apps

# copy supervisord's config
WORKDIR /toskose/supervisord/config
RUN mv /tmp/toskose/apps/supervisord.conf ./supervisord.conf

WORKDIR /toskose/apps
COPY ./toskose-init.sh ./toskose-init.sh
RUN set -eu \
    && chmod +x toskose-init.sh \
    && ./toskose-init.sh ${TOSCA_NODES_SOFTWARE_APPS_NAMES}

### TEST ###
FROM toskosed as toskosed-test
WORKDIR /toskose

RUN set -eu \
    && apt-get update \
    && apt-get install -qq \
    tree \
    && tree -a

### ### ###

FROM toskosed as release

WORKDIR /toskose

VOLUME /toskose/apps /toskose/supervisord/logs

ENTRYPOINT ["/bin/sh", "-c", "/toskose/supervisord/entrypoint.sh"]
