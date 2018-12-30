#!/bin/bash

. base-install.sh

REPOS=(
  https://github.com/Supervisor/supervisor/archive/${SUPERVISOR_VERSION}.tar.gz
)

DIRS=(
  Supervisor-$SUPERVISOR_VERSION
)

# prepare the environment
echo "Initialization.."
for dir in "${DIRS[@]}"
do
  path=${TMP_PATH}/$dir
  isDirExist $path

  if [ "$retval" == 0 ]; then
    echo -e "${path}  ${COLOR_GREEN}already exist${COLOR_RESET}"
  else
    mkdir -p $path
    echo -e "${path}  ${COLOR_GREEN}created${COLOR_RESET}"
  fi
done

# check if repositories are available
echo "Fetching repositories.."
for i in "${!REPOS[@]}" # ! variable indirection
do
  repo=${REPOS[$i]}
  dir=${DIRS[$i]}
  path=${TMP_PATH}/$dir

  retval=$(isOnlineURL $repo)
  if [ "$retval" == 1 ]; then
    echo -e "$repo  ${COLOR_RED}offline${COLOR_RESET}"
    echo -e "${COLOR_RED}Error - Repository cannot be fetched${COLOR_RESET}"
    exit 1
  fi

  echo -e "$repo  ${COLOR_GREEN}online${COLOR_RESET}"
  $fetcher -P $path $repo

  if [ $(find $path \
              -type f \
              -name "*.tgz" -o \
              -name "*.tar.gz" \
              | wc -l) == 1 ]; then

    echo -e "$dir  ${COLOR_GREEN}fetched${COLOR_RESET}"
  else
    echo -e "${COLOR_RED}Error - $dir not fetched${COLOR_RESET}"
    exit 1
  fi
done
