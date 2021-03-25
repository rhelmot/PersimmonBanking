#!/bin/bash

source prod_creds.txt
uwsgi --chdir ./persimmon --wsgi-file persimmon/wsgi.py --master --socket 127.0.0.1:3031 >log.txt 2>&1 & disown
