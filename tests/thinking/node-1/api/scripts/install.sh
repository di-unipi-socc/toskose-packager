#!/bin/sh
git clone -b $API_1_INPUT_BRANCH $API_1_INPUT_REPO /thinking-api
cd /thinking-api
mvn clean install
