#!/bin/bash
. base_test.sh

ROOT_PATH=/test
FETCHER_PATH=/fetcher/data

PATHS=(
  $ROOT_PATH$FETCHER_PATH/supervisor
)

function exist() {
if [ -d $1 ]; then
    echo -e "$1 .. ${COLOR_GREEN}OK${COLOR_RESET}"
else
    echo -e "${COLOR_RED}Error: $1 is empty${COLOR_RESET}"
    exit 1
fi
}

echo "Start data integrity tests.."

for i in "${PATHS[@]}"
do
  exist $i
done
