#!/bin/bash

. scripts/base-install.sh
. scripts/python-install.sh
. scripts/supervisor-install.sh

REPOS=(
  PYTHON_REPOSITORY,
  SUPERVISOR_REPOSITORY
)

# check if repositories are available
echo "Checking repositories.."
for repo in "${REPOS[@]}"
do
  local res=$(isOnlineURL $repo)
  if [ "$res" = false ]; then
    echo -e "${COLOR_RED}Error - Repositories cannot be fetched${COLOR_RESET}"
    exit 1
done







# check for CA certificates (for https)
# TODO



# prepare the environment
# echo "Preparing the environment.."
# for dir in "${SUBDIRS[@]}"
# do
#   mkdir -p $ROOT_PATH/$dir
#   if [ -d $ROOT_PATH/$dir ]; then
#     echo -e "${ROOT_PATH}/${dir}  ${COLOR_GREEN}OK${COLOR_RESET}"
#   else
#     echo -e "${ROOT_PATH}/${dir}  ${COLOR_RED}Error${COLOR_RESET}"
#     exit 1
#   fi
# done
#
# # fetch data from repositories
# echo "Fetching data from repositories.."
# for repo in "${REPOS[@]}"
# do
#   $fetcher
#
#
#
#
#
# TMPDIR=$ROOT_PATH/$SUBDIRS[0]
# $fetcher $TMPDIR $REPOS[0] $REPOS[1]


# install pre-requisites

# install CA certificates

# download python 2.7 tarball

# uncompress the tarball

# install supervisord
