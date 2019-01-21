#!/bin/sh

. "./base.sh"

expected_args=3

find(){

  path=$1
  name=$2

  echo -n "Searching ${name}.."
  if [ $name == ".tar.gz" ]; then
    echo -e "  ${COLOR_RED}KO (missing .tar name)${COLOR_RESET}"
    exit 1
  fi

  if [ ! -f $path/$name ]; then
    echo -e "  ${COLOR_RED}KO (not found)${COLOR_RESET}"
    exit 1
  else
    echo -e "  ${COLOR_GREEN}OK${COLOR_RESET}"
  fi
}

untar(){

  in_path=$1
  name=$2
  out_path=$3

  echo -n "Untaring ${name}.."
  if [ $(tar -zxf $in_path/$name -C $out_path --strip-components=1) > /dev/null ]; then
    echo -e "  ${COLOR_RED}KO (failed)${COLOR_RESET}"
    exit 1
  else
    echo -e "  ${COLOR_GREEN}OK${COLOR_RESET}"
  fi
}

# Arguments Checking
checkExpectedArgs $# $expected_args

# check path
in_path=$1
err_msg="input path not supplied"
checkStringIsEmptyOrNull $in_path $err_msg

# check archive name
name=$2
err_msg="filename not supplied"
checkStringIsEmptyOrNull $name $err_msg

# check output path
out_path=$3
err_msg="output ppath not supplied"
checkStringIsEmptyOrNull $name $err_msg

# searching archive
find $in_path $name

# untar archive
untar $in_path $name $out_path
