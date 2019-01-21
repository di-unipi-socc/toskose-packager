#!/bin/sh

. "./base.sh"

expected_args=2

fetcher=$(
  if hash wget 2> /dev/null; then echo "wget -q";
  else
    echo "wget not installed. Cannot fetch dependencies. Abort"
    exit 1
  fi
);

isOnline(){

  local URL=$1
  $fetcher --spider $URL

  echo "Checking $URL.."
  if [ $? -eq 0 ]; then
    echo -e "${URL}  ${COLOR_GREEN}online${COLOR_RESET}"
  else
    echo -e "${URL}  ${COLOR_RED}offline${COLOR_RESET}"
    exit 1
  fi
}

isDirExist(){

  local DIR=$1

  echo "Checking $DIR .."
  if [ -d $DIR ]; then
    echo -e "${DIR}  ${COLOR_GREEN}OK${COLOR_RESET}"
  else
    echo -e "${DIR}  ${COLOR_RED}KO${COLOR_RESET}"
    exit 1
  fi
}

# Arguments Checking
checkExpectedArgs $# $expected_args

# Check repository status
URL=$1
err_msg="URL not supplied"
checkStringIsEmptyOrNull $URL $err_msg

isOnline $URL

# Check destination
DEST=$2
err_msg="Destination not supplied"
checkStringIsEmptyOrNull $DEST $err_msg

isDirExist $DEST

echo -n "Fetching data.."
$fetcher -P $DEST $URL

if [ $? -eq 0 ]; then
  echo -e "  ${COLOR_GREEN}OK${COLOR_RESET}"
else
  echo -e "  ${COLOR_RED}KO${COLOR_RESET}"
  exit 1
fi
