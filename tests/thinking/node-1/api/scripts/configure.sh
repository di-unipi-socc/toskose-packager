#!/bin/sh
TARGET=/thinking-api/api-config.yml
echo dbURL: '"'$API_1_INPUT_DBURL'"' > $TARGET
echo dbPort: '"'$API_1_INPUT_DBPORT'"' >> $TARGET
echo dbName: '"'$API_1_INPUT_DBNAME'"' >> $TARGET
echo collectionName: '"'$API_1_INPUT_COLLECTIONNAME'"' >> $TARGET
