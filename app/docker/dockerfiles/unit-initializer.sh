#!/bin/sh

# Initialize the root dirs of the components hosted on the container.
cd /toskose/apps
for d in */ ; do
    echo "creating root dir for ${d}.."
    mkdir -p /$d
done