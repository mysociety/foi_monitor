#!/usr/bin/env python
"""
script for manually running various commands, not meant to be 
in regular use
"""
import os
import sys

try:
    os.environ.pop("DJANGO_SETTINGS_MODULE")
except Exception:
    pass

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proj.settings")
django.setup()


from pi_monitor.populate import populate

if __name__ == "__main__":
    populate()
