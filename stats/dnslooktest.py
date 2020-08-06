#!/usr/bin/python
# coding=utf-8
#
# The module dnslookup assesses properties of a domain name: find its root zone, find who manages it,
# find whether the name is an alias, resolve the chain of aliases, find who serves the IP address.
# The goal is to observe concentration in both the name services and the distribution services.
#
# For name services, we capture the list of NS servers for the specified name.
# For distribution services, we capture the list of CNames and the IP addresses.
# We format the results as a JSON entry.
#
# The procedures are embedded in the class "dnslook", with three main methods:
#
# get_domain_data(self, domain): read from the DNS the data for the specified domain, and 
# store the results in the referenced object.
# 
# to_json(self): serialize the object as a JSON string.
#
# from_json(self, js): load the object value from a JSON string. 

import sys
import dns.resolver
import json
import traceback
import dnslook

# Basic tests

if len(sys.argv) != 2:
    print("Usage: " + argv[0] + " domain-name")
    exit(1)

domain = sys.argv[1]
v = dnslook.dnslook()
v.get_domain_data(domain)
js = v.to_json()
print(js)
w = dnslook.dnslook()
if w.from_json(js):
    js2 = w.to_json()
    if js2 == js:
        print("Parsed json matches input")
    else:
        print("Converted from json differs:")
        print(js2)
else:
    print("Cannot parse json output")