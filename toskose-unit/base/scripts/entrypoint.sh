#!/bin/bash

/toskose/supervisord/bundle/supervisord \
-c /toskose/supervisord/config/supervisord.conf \
-l /toskose/supervisord/logs/supervisord.log
