#!/usr/bin/python
# coding=utf-8
#
# This script extracts dns server statictics from the results file.

import sys
import dns.resolver
import dnslook
import traceback
import ipaddress
import ip2as
import publicsuffix

class ns_item_line:
    def __init__(self):
        self.count = 0
        self.weighted = 0.0
        self.name = ""

    def compare(self, other):
        if (self.weighted > other.weighted):
            return -1
        elif (self.weighted < other.weighted):
            return 1
        elif (self.count > other.count):
            return -1
        elif (self.count < other.count):
            return 1
        elif (self.name < other.name):
            return -1
        elif (self.name > other.name):
            return 1
        else:
            return 0

    def __lt__(self, other):
        return self.compare(other) < 0
    def __gt__(self, other):
        return self.compare(other) > 0
    def __eq__(self, other):
        return self.compare(other) == 0
    def __le__(self, other):
        return self.compare(other) <= 0
    def __ge__(self, other):
        return self.compare(other) >= 0
    def __ne__(self, other):
        return self.compare(other) != 0         


if len(sys.argv) != 4:
    print("Usage: " + sys.argv[0] + " public_suffix_file domain_list_file dns_stats_file")
    exit(1)

public_suffix_file = sys.argv[1]
domain_list_file = sys.argv[2]
dns_stats_file = sys.argv[3]

ps = publicsuffix.public_suffix()
if not ps.load_file(public_suffix_file):
    print("Could not load the suffixes")
    exit(1)

nb_lines = 0
nb_ns_domains = 0
nb_pns_domains = 0
nb_pns_total = 0
ns_dict = dict()

try:
    for line in open(domain_list_file , "rt"):
        nb_lines += 1 
        d = dnslook.dnslook()
        if d.from_json(line):
            if len(d.ns) > 0:
                nb_ns_domains += 1
                local_ns = dict()
                n_pns = 0
                for xns in d.ns:
                    pns = ps.suffix(xns)
                    if len(pns) > 0:
                        if pns.startswith("awsdns"):
                            pns = "awsdns"
                        elif pns.startswith("azure-dns"):
                            pns = "azure-dns"
                        elif pns.startswith("ultradns"):
                            pns = "ultradns"
                        n_pns += 1
                        if pns in local_ns:
                            local_ns[pns] += 1
                        else:
                            local_ns[pns] = 1
                if n_pns > 0:
                    nb_pns_domains += 1
                    for pns in local_ns:
                        nb_pns_total += 1
                        if pns in ns_dict:
                            ns_dict[pns].count += 1
                            ns_dict[pns].weighted += local_ns[pns]/n_pns
                        else:
                            item = ns_item_line()
                            item.count = 1
                            item.weighted = local_ns[pns]/n_pns
                            item.name = pns
                            ns_dict[pns] = item
except Exception as e:
    traceback.print_exc()
    print("Cannot read file \"" + domain_list_file  + "\"\nException: " + str(e))
    print("Giving up");
    exit(1)

nb_ns = len(ns_dict)
print("Done counting NS")
print("Nb_lines: " + str(nb_lines))
print("Nb_ns_domains: " + str(nb_ns_domains))
print("Nb_pns_domains: " + str(nb_pns_domains))
print("Nb_pns_total: " + str(nb_pns_total))
print("Nb_ns: " + str(nb_ns))

if nb_ns == 0:
    print("No NS found in \"" + domain_list_file  + "\"\n")
    print("Giving up");
    exit(1)

ns_list = sorted(ns_dict.values())
n_cumul = 0
s_cumul = 0.0
nb_written = 0

try:
    f_ns = open(dns_stats_file , "wt", encoding="utf-8")
    f_ns.write("name, n_ref, n_cumul, n%, n_cumul%, n_weighted, w_cumul, w%, w_cumul%\n")
    for p in ns_list:
        n_cumul += p.count
        n_frac = p.count/nb_pns_total
        n_c_frac = n_cumul/nb_pns_total
        s_cumul += p.weighted
        s_frac = p.weighted/nb_pns_domains
        s_c_frac = s_cumul/nb_pns_domains
        f_ns.write(p.name + "," + \
             str(p.count) + "," + str(n_cumul) + "," + \
             str(100*n_frac) + "%," + str(100*n_c_frac) + "%," + \
             str(p.weighted) + "," + str(s_cumul) + "," + \
             str(100*s_frac) + "%," + str(100*s_c_frac) + "%\n")
        nb_written += 1
    f_ns.close()
except Exception as e:
    traceback.print_exc()
    print("Cannot create file <" + dns_stats_file  + ">\nException: " + str(e))
    print("Giving up");
    exit(1)

print("nb_dns_written: " + str(nb_written))
