#!/bin/bash

if [ ! -f /app/databases/db.sqlite3 ]; then
    cd /app
    python manage.py migrate
    python manage.py populate
fi
