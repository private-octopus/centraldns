#!/usr/bin/python
# coding=utf-8
#
# The module dnslookup assesses properties of a domain name: find its root zone, find who manages it,
# find whether the name is an alias, resolve the chain of aliases, find who serves the IP address.
# The goal is to observe concentration in both the name services and the distribution services.
#
# For name services, we capture the list of NS servers for the specified name.
# For distribution services, we capture the list of CNames and the IP addresses.
# We also compute the "server name" and the AS Number. The server name is defined as the public suffix
# of the last CNAME, or that of the actual name if there are no CNAME. The AS Number is that of the
# first IPv4 address returned in the list.
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
import publicsuffix
import ip2as

class dnslook:
    def __init__(self):
        self.domain = ""
        self.ip = []
        self.ipv6 = []
        self.zone = ""
        self.ns = []
        self.cname = []
        self.server = ""
        self.as_number = 0

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
        js = "{\"domain\":\"" + self.domain + "\""
        js += ",\"ip\":" + dnslook.to_json_array(self.ip)       
        js += ",\"ipv6\":" + dnslook.to_json_array(self.ipv6)
        js += ",\"zone\":\"" + self.zone + "\""
        js += ",\"ns\":" + dnslook.to_json_array(self.ns)
        js += ",\"cname\":" + dnslook.to_json_array(self.cname)
        js += ",\"server\":\"" + self.server + "\""
        if self.as_number > 0:
            js += ",\"as_number\":" + str(self.as_number)
        js += "}"
        return(js)
    
    def from_json(self, js):
        ret = True
        try:
            jd = json.loads(js)
            if not 'domain' in jd:
                ret = False
            else:
                self.__init__()
                self.domain = jd['domain']
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
                if 'server' in jd:
                    self.server = jd['server']
                if 'as_number' in jd:
                    self.as_number = jd['as_number']
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

    def get_server(self, ps, test=False):
        if len(ps.table) > 0:
            if len(self.cname) == 0:
                self.server = ps.suffix(self.domain)
                if test:
                    print("No cname. Domain: \"" + self.domain + "\", server: \"" + self.server + "\"")
            else:
                self.server = ps.suffix(self.cname[-1])
                if test:
                    print("Cname[-1]: \"" + self.cname[-1] + "\", server: \"" + self.server + "\"")
        elif test:
            print("Empty table.")

    def get_asn(self, i2a):
        if len(i2a.table) > 0 and len(self.ip) > 0:
            self.as_number = i2a.get_asn(self.ip[0])

    def get_domain_data(self, domain, ps, i2a):
        self.domain = domain
        self.get_a()
        self.get_aaaa()
        self.get_ns()
        self.get_cname()
        self.get_server(ps)
        self.get_asn(i2a)
