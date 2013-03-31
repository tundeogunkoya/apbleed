#!/usr/bin/python
#
# AP tests
# Copyright (c) 2013, Jouni Malinen <j@w1.fi>
#
# This software may be distributed under the terms of the BSD license.
# See README for more details.

import os
import re
import sys
import time

import logging

from wpasupplicant import WpaSupplicant
from hostapd import HostapdGlobal

def reset_devs(dev, apdev):
    for d in dev:
        d.reset()
    hapd = HostapdGlobal()
    for ap in apdev:
        hapd.remove(ap['ifname'])

def main():
    idx = 1
    if len(sys.argv) > 1 and sys.argv[1] == '-d':
        logging.basicConfig(level=logging.DEBUG)
        idx = idx + 1
    elif len(sys.argv) > 1 and sys.argv[1] == '-q':
        logging.basicConfig(level=logging.WARNING)
        idx = idx + 1
    else:
        logging.basicConfig(level=logging.INFO)

    if len(sys.argv) > idx:
        test_filter = sys.argv[idx]
    else:
        test_filter = None

    dev0 = WpaSupplicant('wlan0')
    dev1 = WpaSupplicant('wlan1')
    dev2 = WpaSupplicant('wlan2')
    dev = [ dev0, dev1, dev2 ]
    apdev = [ ]
    apdev.append({"ifname": 'wlan3', "bssid": "02:00:00:00:03:00"})
    apdev.append({"ifname": 'wlan4', "bssid": "02:00:00:00:04:00"})

    for d in dev:
        if not d.ping():
            print d.ifname + ": No response from wpa_supplicant"
            return
        d.reset()
        print "DEV: " + d.ifname + ": " + d.p2p_dev_addr()
    for ap in apdev:
        print "APDEV: " + ap['ifname']

    tests = []
    for t in os.listdir("."):
        m = re.match(r'(test_.*)\.py$', t)
        if m:
            print "Import test cases from " + t
            mod = __import__(m.group(1))
            for s in dir(mod):
                if s.startswith("test_"):
                    func = mod.__dict__.get(s)
                    tests.append(func)

    passed = []
    failed = []

    for t in tests:
        if test_filter:
            if test_filter != t.__name__:
                continue
        reset_devs(dev, apdev)
        print "START " + t.__name__
        if t.__doc__:
            print "Test: " + t.__doc__
        for d in dev:
            d.request("NOTE TEST-START " + t.__name__)
        try:
            if t.func_code.co_argcount > 1:
                t(dev, apdev)
            else:
                t(dev)
            passed.append(t.__name__)
            print "PASS " + t.__name__
        except Exception, e:
            print e
            failed.append(t.__name__)
            print "FAIL " + t.__name__
        for d in dev:
            d.request("NOTE TEST-STOP " + t.__name__)

    if not test_filter:
        reset_devs(dev, apdev)

    print "passed tests: " + str(passed)
    print "failed tests: " + str(failed)
    if len(failed):
        sys.exit(1)

if __name__ == "__main__":
    main()