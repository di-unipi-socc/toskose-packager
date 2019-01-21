#!/bin/bash

# notification colors
COLOR_RED='\e[31m'
COLOR_GREEN='\e[32m'
COLOR_RESET='\e[0m'

# check if wget or curl are pre-installed
fetcher=$(
  if hash wget 2> /dev/null; then
    echo "wget -q"
  else
    echo -e "wget not installed. Cannot fetch dependencies. Abort"
    exit 1
  fi
);

# check if a dir exists
isDirExist(){
  if [ -d "$1" ]; then
    retval=0
  else
    retval=1
  fi
}

# check if an URL is available
isOnlineURL(){
  $fetcher --spider $1

  if [ $? == 0 ]; then
    retval=0
  else
    retval=1
  fi
}
