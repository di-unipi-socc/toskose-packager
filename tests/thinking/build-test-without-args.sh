#!/bin/bash

docker build -t stephenreed/jenkins-java8-maven-git-toskosed:latest \
--build-arg TOSKOSE_UNIT_IMAGE=diunipisocc/toskose-unit:latest \
--build-arg TOSCA_NODES_CONTAINER_IMAGE=stephenreed/jenkins-java8-maven-git:latest \
--build-arg TOSCA_NODES_SOFTWARE_APPS_NAMES=api \
--build-arg TOSCA_NODES_SOFTWARE_STUFF_PATH=./node-1/ \
-f Dockerfile .