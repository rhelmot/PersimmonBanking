#!/bin/bash

if pgrep uwsgi; then
	echo 'UWSGI is already running.'
	exit 1
fi

touch reload.touch

uwsgi --chdir ./persimmon --wsgi-file persimmon/wsgi.py --master --touch-reload $(realpath reload.touch) --socket 127.0.0.1:3031 >>log.txt 2>&1 & disown
