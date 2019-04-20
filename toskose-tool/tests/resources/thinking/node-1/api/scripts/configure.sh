#!/bin/sh
TARGET=/thinking-api/api-config.yml
echo dbURL: '"'$API_INPUT_DBURL'"' > $TARGET
echo dbPort: '"'$API_INPUT_DBPORT'"' >> $TARGET
echo dbName: '"'$API_INPUT_DBNAME'"' >> $TARGET
echo collectionName: '"'$API_INPUT_COLLECTIONNAME'"' >> $TARGET
