#!/bin/bash

# abort on any errors
set -e

# check that we are in the expected directory
cd `dirname $0`/..

# Upgrade pip to a secure version
pip_version="$(pip3 --version)"
if [ "$(echo -e 'pip3 1.4\n'"$pip_version" | sort -V | head -1)" = "$pip_version" ]; then
    curl -L -s https://bootstrap.pypa.io/get-pip.py | python
fi

# Upgrade setuptools, to avoid "invalid environment marker" error from
# cryptography package. https://github.com/ansible/ansible/issues/31741
sudo pip3 install --upgrade setuptools

pip3 install --requirement requirements.txt

# make sure that there is no old code (the .py files may have been git deleted)
find . -name '*.pyc' -delete