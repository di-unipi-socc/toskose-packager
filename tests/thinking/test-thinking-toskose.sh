#!/bin/bash

docker build -t test-thinking-toskose \
--build-arg TOSKOSE_UNIT_IMAGE=toskose-unit-base:1.0.0 \
--build-arg TOSCA_NODES_CONTAINER_IMAGE=stephenreed/jenkins-java8-maven-git:latest \
--build-arg TOSCA_NODES_SOFTWARE_APPS_NAMES=api \
--build-arg TOSCA_NODES_SOFTWARE_STUFF_PATH=./node-1/ \
.