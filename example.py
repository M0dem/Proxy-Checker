#!/usr/bin/env python

from proxychecker import ProxyChecker

inlist = [
    "202.100.167.142:80",
    "101.200.182.29:3128",
    "37.128.116.34:3128",
    "80.96.203.117:9999",
    "120.27.118.141:3128",
    "216.100.91.250:3128",
    "54.190.196.251:8018",
    "104.238.83.28:443",
    "200.9.220.94:3128",
    "137.135.166.225:8128"
]

proxy_checker = ProxyChecker(inlist, verbose = True)
outlist = proxy_checker.start()

# if there are any proxies in our output list, list them
if outlist:
    print("Working proxies from list:")
    for proxy in outlist:
        print("\t" + proxy)
