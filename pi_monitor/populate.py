#!/usr/bin/env python
import datetime
from pi_monitor.models import Jurisdiction


def populate():
    print ("running population")
    Jurisdiction.populate()
