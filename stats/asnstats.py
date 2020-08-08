#!/usr/bin/python
# coding=utf-8
#
# This script extracts per ASN statictics from the results file.

import sys
import dns.resolver
import dnslook
import traceback

if len(sys.argv) != 3:
    print("Usage: " + sys.argv[0] + " domain_list_file asn_stats_file")
    exit(1)

domain_list_file = sys.argv[1]
asn_stats_file = sys.argv[2]

asn_list = dict()

nb_lines = 0
nb_domains = 0


try: 
    for line in open(domain_list_file , "rt"):
        nb_lines += 1 
        d = dnslook.dnslook()
        if d.from_json(line):
            nb_domains += 1
            if d.as_number in asn_list:
                asn_list[d.as_number] += 1
            else:
                asn_list[d.as_number] = 1
    print("All done")
except Exception as e:
    traceback.print_exc()
    print("Cannot read file \"" + domain_list_file  + "\"\nException: " + str(e))
    print("Giving up");
    exit(1)


print("nb_lines: " + str(nb_lines))
print("nb_domains: " + str(nb_domains))
print("nb_asn: " + str(len(asn_list)))

if nb_domains == 0:
    print("Did not find any domain in \"" + domain_list_file  + "\"")
    print("Giving up");
    exit(1)

nb_written = 0
nb_total = 0
try:
    f_out = open(asn_stats_file, "wt")
    f_out.write(" ASN, Count, Share,\n")
    for asn in asn_list:
        share = asn_list[asn]/nb_domains;
        f_out.write(str(asn) + "," + str(asn_list[asn]) + "," + str(share) + ",\n")
        nb_written += 1
        nb_total += asn_list[asn]
    f_out.close()
except Exception as e:
    traceback.print_exc()
    print("Cannot create file <" + asn_stats_file  + ">\nException: " + str(e))
    print("Giving up");
    exit(1)

print("nb_asn_written: " + str(nb_written))
print("nb_domains_counted: " + str(nb_total))
exit(0)



f_out.close()
