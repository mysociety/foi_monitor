#!/usr/bin/env python
from pi_monitor.models import Jurisdiction


def populate():
    print("running population")
    Jurisdiction.populate()
