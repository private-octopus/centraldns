#!/usr/bin/python
# coding=utf-8
#
# The module dnslookup assesses properties of a domain name: find its root zone, find who manages it,
# find whether the name is an alias, resolve the chain of aliases, find who serves the IP address.

import sys
import dns.resolver

if len(sys.argv) != 2:
    print("Usage: " + argv[0] + " domain-name")
    exit(1)

domain = sys.argv[1]

try:
    addresses = dns.resolver.query(domain, 'A')
    for ipval in addresses:
        print('IP', ipval.to_text())
except Exception as e:
    pass

try:
    addresses6 = dns.resolver.query(domain, 'AAAA')
    for ipval6 in addresses6:
        print('IPv6', ipval6.to_text())
except Exception as e:
    pass

nameparts = domain.split(".")
while len(nameparts) > 1 :
    zone = ""
    for p in nameparts:
        zone += p
        zone += '.'
    try:
        nameservers = dns.resolver.query(zone, 'NS')
        print('zone', zone)
        for nsval in nameservers:
            print('NS', nsval.to_text())
        break
    except Exception as e:
        nameparts.pop(0)


candidates = [ domain ]
locations = []
while len(candidates) > 0:
    x =  candidates[0]
    candidates.pop(0)
    try:
        aliases = dns.resolver.query(x, 'CNAME')
        for cnameval in aliases:
            print (' cname target address:' + str(cnameval.target))
            candidates.append(str(cnameval.target))
    except Exception as e:
        locations.append(x)
print("locations for " + domain)
for location in locations:
    print(location)

# TODO: BGP table from https://bgp.potaroo.net/as6447/bgptable.txt (or other AS)
# FOrmat: 1.0.0.0/24 147.28.7.2 3130 2914 13335
#         subnet     next hop    as    as  as (owner of IP)
# sometimes ">" before first line.
