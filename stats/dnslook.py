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

import sys
import dns.resolver
import json
import traceback

class dnslook:
    def __init__(self):
        self.domain = ""
        self.ip = []
        self.ipv6 = []
        self.zone = ""
        self.ns = []
        self.cname = []

    def to_json_array(x):
        jsa = "["
        is_first = True
        for item in x:
            if not is_first:
                jsa += ","
            is_first = False
            jsa += "\"" + str(item) + "\""
        jsa += "]"
        return(jsa)

    def to_json(self):
        js = "{\"name\":\"" + domain + "\""
        js += ",\"ip\":" + dnslook.to_json_array(self.ip)       
        js += ",\"ipv6\":" + dnslook.to_json_array(self.ipv6)
        js += ",\"zone\":\"" + self.zone + "\""
        js += ",\"ns\":" + dnslook.to_json_array(self.ns)
        js += ",\"cname\":" + dnslook.to_json_array(self.cname)
        js += "}"
        return(js)
    
    def from_json(self, js):
        ret = True
        try:
            jd = json.loads(js)
            if not 'name' in jd:
                ret = False
            else:
                self.__init__()
                self.name = jd['name']
                if 'ip' in jd:
                    self.ip = jd['ip']
                if 'ipv6' in jd:
                    self.ipv6 = jd['ipv6']
                if 'zone' in jd:
                    self.zone = jd['zone']
                if 'ns' in jd:
                    self.ns = jd['ns']
                if 'cname' in jd:
                    self.cname = jd['cname']
        except Exception as e:
            traceback.print_exc()
            print("Cannot parse <" + js + ">")
            print("error: " + str(e));
            ret = False
        return(ret)


    def get_a(self):
        self.ip = []
        try:
            addresses = dns.resolver.query(self.domain, 'A')
            for ipval in addresses:
                self.ip.append(ipval.to_text())
        except Exception as e:
            pass

    def get_aaaa(self):
        self.ipv6 = []
        try:
            addresses = dns.resolver.query(self.domain, 'AAAA')
            for ipval in addresses:
                self.ipv6.append(ipval.to_text())
        except Exception as e:
            pass

    def get_ns(self):
        self.ns = []
        nameparts = self.domain.split(".")
        while len(nameparts) > 1 :
            self.zone = ""
            for p in nameparts:
                self.zone += p
                self.zone += '.'
            try:
                nameservers = dns.resolver.query(self.zone, 'NS')
                for nsval in nameservers:
                    self.ns.append(nsval.to_text())
                break
            except Exception as e:
                nameparts.pop(0)

    def get_cname(self):
        self.cname = []
        candidate = self.domain
        while True:
            try:
                aliases = dns.resolver.query(candidate, 'CNAME')
                if len(aliases) > 0:
                    candidate = aliases[0].to_text()
                    self.cname.append(candidate)
                else:
                    break
            except Exception as e:
                break

    def get_domain_data(self, domain):
        self.domain = domain
        self.get_a()
        self.get_aaaa()
        self.get_ns()
        self.get_cname()
            


# Basic tests

if len(sys.argv) != 2:
    print("Usage: " + argv[0] + " domain-name")
    exit(1)

domain = sys.argv[1]
v = dnslook()
v.get_domain_data(domain)
js = v.to_json()
print(js)
w = dnslook()
if w.from_json(js):
    js2 = w.to_json()
    if js2 == js:
        print("Parsed json matches input")
    else:
        print("Converted from json differs:")
        print(js2)
else:
    print("Cannot parse json output")