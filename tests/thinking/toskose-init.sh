#!/bin/bash

IFS=':' read -a names <<< "$1"

# remove the toskose-unit's test app example
rm -rf test/
# move apps's dirs containing scripts/ into /toskose/apps/
mv /tmp/toskose/apps/* /toskose/apps/

for name in "${names[@]}"
do
  set -eu

  # initialize logs
  mkdir -p /toskose/apps/${name}/logs
  touch /toskose/apps/${name}/logs/${name}.log

  # app lifecyle scripts executable
  chmod -R 777 /toskose/apps/${name}/scripts/
done
