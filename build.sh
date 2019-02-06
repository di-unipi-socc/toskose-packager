#!/bin/bash

type=$1
version=$2

if [ -z "${type}" ]; then
    echo "missing operation type (unit | manager)"
    exit 1
fi

if [ -z "${version}" ]; then
    echo "missing version"
    exit 1
fi

if [ "${type}" == 'unit' ]; then

    echo "build toskose-unit image (version: ${type}).."
    docker build \
    -t diunipisocc/toskose-unit:${version} \
    --build-arg APP_VERSION=${version} \
    --build-arg PYTHON_VERSION=2.7.15 \
    --build-arg SUPERVISORD_VERSION=3.3.5 \
    --build-arg DEBIAN_VERSION=stretch \
    -f toskose-unit/Dockerfile toskose-unit/.

elif [ "${type}" == 'manager' ]; then

    echo "build toskose-manager image (version: ${version}).."
    docker build \
    -t diunipisocc/toskose-manager:${version} \
    --build-arg PYTHON_VERSION=3.7.2 \
    --build-arg APP_VERSION=${version} \
    -f toskose-manager/api/Dockerfile toskose-manager/api/.
    
else
    echo "operation type not recognized"
    exit 1
fi

echo "generating the latest version.."
docker tag diunipisocc/toskose-${type}:${version} diunipisocc/toskose-${type}:latest

echo "pushing on the repository.."
docker push diunipisocc/toskose-${type}:${version}
docker push diunipisocc/toskose-${type}:latest