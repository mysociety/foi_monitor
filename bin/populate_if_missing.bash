#!/bin/bash

set -e

cd "$(dirname "$0")/.."

if [ ! -f ./conf/config.py ] ; then
    cp conf/config.py-example conf/config.py
fi

if [ ! -f /app/databases/db.sqlite3 ]; then
    python manage.py migrate
    python manage.py populate
fi
