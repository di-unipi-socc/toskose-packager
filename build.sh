#!/bin/bash

echo "build toskose-unit image"
docker build \
-t toskose-unit-base:1.0.0 \
--build-arg APP_VERSION=1.0.0 \
--build-arg PYTHON_VERSION=2.7.15 \
--build-arg SUPERVISORD_VERSION=3.3.5 \
--build-arg DEBIAN_VERSION=stretch \
-f toskose-unit/Dockerfile .

echo "build toskose-manager image"
docker build \
-t toskose-manager:1.0.0 \
--build-arg APP_VERSION=1.0.0 \
-f toskose-manager/Dockerfile .
