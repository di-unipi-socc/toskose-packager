#!/bin/bash

MAVEN_IMAGE="giulen/thinking-maven-toskosed"
NODE_IMAGE="giulen/thinking-node-toskosed"
MONGODB_IMAGE="giulen/thinking-mongodb-toskosed"
MANAGER_IMAGE="giulen/thinking-manager"

# TODO Sockshop

images=( $MAVEN_IMAGE $NODE_IMAGE $MONGODB_IMAGE $MANAGER_IMAGE )

docker --version
echo "$DOCKER_PASSWORD" | docker login --username "$DOCKER_USERNAME" --password-stdin

for image in "${images[@]}"
do
    docker push $image
done