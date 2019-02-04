#!/bin/bash

. base-install.sh

REPOS=(
  https://github.com/Supervisor/supervisor/archive/${SUPERVISOR_VERSION}.tar.gz
)

REPOS_NAMES=(
  "Supervisor-${SUPERVISOR_VERSION}"
)

PATHS=(
  "${TMP_PATH}/supervisor"
)

# check if repositories are available
echo "Fetching repositories.."
for i in "${!REPOS[@]}" # ! variable indirection
do
  repo=${REPOS[$i]}

  retval=$(isOnlineURL ${repo})
  if [ "$retval" == 1 ]; then
    echo -e "$repo  ${COLOR_RED}offline${COLOR_RESET}"
    echo -e "${COLOR_RED}Error - Repository cannot be fetched${COLOR_RESET}"
    exit 1
  fi

  echo -e "$repo  ${COLOR_GREEN}online${COLOR_RESET}"
  echo "Start downloading ${REPOS_NAMES[$i]}.."
  ${fetcher} -P ${PATHS[$i]} ${repo}

  if [ $(find ${PATHS[$i]} \
              -type f \
              -name "*.tgz" -o \
              -name "*.tar.gz" \
              | wc -l) == 1 ]; then

    echo -e "${REPOS_NAMES[$i]} ${COLOR_GREEN}fetched${COLOR_RESET}"
  else
    echo -e "${COLOR_RED}Error - ${REPOS_NAMES[$i]} not fetched${COLOR_RESET}"
    exit 1
  fi
done
