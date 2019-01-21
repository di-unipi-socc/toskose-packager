#!/bin/sh

# Color Management
COLOR_RED='\e[31m'
COLOR_GREEN='\e[32m'
COLOR_YELLOW='\e[33m'
COLOR_RESET='\e[0m'

# Arguments Checking
checkExpectedArgs(){
  n_args=$1
  expected=$2
  if [ $n_args -lt $expected ];
    then echo -e "${COLOR_RED}Missing arguments${COLOR_RESET}"
    exit 1
  elif [ $n_args -gt $expected ];
    then echo -e "${COLOR_YELLOW}More arguments then expected.. they will be ignored${COLOR_RESET}"
  fi
}

# String Checking
checkStringIsEmptyOrNull(){
  str=$1
  err_msg=$2
  if [ -z "$str" ];
    then echo -e "${COLOR_RED}${err_msg}${COLOR_RESET}"
    exit 1
  fi

}
