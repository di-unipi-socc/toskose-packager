#!/bin/bash

/usr/bin/supervisord \
-c /toskose/config/supervisord.conf \
-l /var/log/supervisor.log