#!/bin/bash

type=$1
version=$2

usage_msg="usage: ./build.sh [unit|manager] [VERSION]\nexample: ./build.sh manager 1.0.2\n"

if [ -z "${type}" ]; then
    printf "missing operation type\n${usage_msg}"
    exit 1
fi

if [ -z "${version}" ]; then
    printf "missing version\n${usage_msg}"
    exit 1
fi

if [ "${type}" == 'unit' ]; then

    printf "build toskose-unit image (version: ${type}).."
    docker build \
    -t diunipisocc/toskose-unit:${version} \
    --build-arg APP_VERSION=${version} \
    --build-arg PYTHON_VERSION=2.7.15 \
    --build-arg SUPERVISORD_VERSION=3.3.5 \
    --build-arg DEBIAN_VERSION=stretch \
    -f toskose-unit/Dockerfile toskose-unit/.

elif [ "${type}" == 'manager' ]; then

    printf "build toskose-manager image (version: ${version}).."
    docker build \
    -t diunipisocc/toskose-manager:${version} \
    --build-arg PYTHON_VERSION=3.7.2 \
    --build-arg APP_VERSION=${version} \
    -f toskose-manager/api/Dockerfile toskose-manager/api/.
    
else
    printf "operation type not recognized\n${usage_msg}"
    exit 1
fi

printf "generating the latest version.."
docker tag diunipisocc/toskose-${type}:${version} diunipisocc/toskose-${type}:latest

printf "pushing on the repository.."
docker push diunipisocc/toskose-${type}:${version}
docker push diunipisocc/toskose-${type}:latest