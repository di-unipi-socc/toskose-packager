#!/bin/bash

COLOR_RED='\e[31m'
COLOR_GREEN='\e[32m'
COLOR_RESET='\e[0m'

PYTHON_VERSION=${PYTHON_VERSION:-2.7.15}
SUPERVISOR_VERSION=${SUPERVISOR_VERSION:-3.3.4}

REPOS=(
  https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz
  https://github.com/Supervisor/supervisor/archive/${SUPERVISOR_VERSION}.tar.gz
)

ROOT_PATH=/toskose
SUBDIRS=(
  tmp,
  python,
  supervisor
)

# check for CA certificates (for https)
# TODO

# check if wget or curl are pre-installed
fetcher=$(
  if hash wget 2> /dev/null; then echo "wget -q";
  else
    echo "wget not installed. Cannot fetch dependencies. Abort"
    exit 1
  fi
);

# check if repositories are available
isOnline(){
  if [ $? -eq 0 ]; then 
    echo -e "[${COLOR_GREEN}online${COLOR_RESET}]"
  else
    echo -e "[${COLOR_RED}offline${COLOR_RESET}]"
  fi
}
echo "Checking repositories.."
for repo in "${REPOS[@]}"
do
  $fetcher --spider $repo
  echo -e "${repo}  $(isOnline)"
done

# prepare the environment
echo "Preparing the environment.."
for dir in "${SUBDIRS[@]}"
do
  mkdir -p $ROOT_PATH/$dir
  if [ -d $ROOT_PATH/$dir ]; then
    echo -e "${ROOT_PATH}/${dir}  ${COLOR_GREEN}OK${COLOR_RESET}"
  else
    echo -e
    exit 1
  fi
done

echo "Fetching repositories.."
TMPDIR=$ROOT_PATH/$SUBDIRS[0]
$fetcher $TMPDIR $REPOS[0] $REPOS[1]


# install pre-requisites

# install CA certificates

# download python 2.7 tarball

# uncompress the tarball

# install supervisord
