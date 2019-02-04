# notification colors
COLOR_RED='\e[31m'
COLOR_GREEN='\e[32m'
COLOR_RESET='\e[0m'

# check if wget or curl are pre-installed
fetcher=$(
  if hash wget 2> /dev/null; then echo "wget -q";
  else
    echo -e "wget not installed. Cannot fetch dependencies. Abort"
    exit 1
  fi
);

# URLs notifications about their state (online/offline)
isOnlineNotify(){
  if [ $? -eq 0 ]; then
    echo -e "[${COLOR_GREEN}online${COLOR_RESET}]"
  else
    echo -e "[${COLOR_RED}offline${COLOR_RESET}]"
  fi
}

# check if an URL is available
isOnlineURL(){
  $fetcher --spider $1
  echo -e "$1  $(isOnlineNotify)"

  if [ $? -eq 0 ]; then
    return true
  else
    return false
}
