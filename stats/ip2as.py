#!/usr/bin/python
# coding=utf-8
#
# Build an IP Address to AS number conversion tool.
# Start with a BGP table, then produce an ordered list of ip addresses.
# Lookup will load this ordered list and answer the question.
# Get the BGP table from https://bgp.potaroo.net/as6447/bgptable.txt (or other AS)
# Format: 1.0.0.0/24 147.28.7.2 3130 2914 13335
#         subnet     next hop    as    as  as (owner of IP)
# sometimes ">" before first line.

import sys
import traceback
import ipaddress

class ipdom_line:
    def __init__(self):
        self.prefix_length = 0
        self.as_number = 0
        self.duplicates = 0
        self.ip_first = ipaddress.ip_address("0.0.0.0")
        self.ip_last = ipaddress.ip_address("255.255.255.255")

    def compare(self, other):
        if (self.ip_first < other.ip_first):
            return -1
        elif (self.ip_first > other.ip_first):
            return 1
        elif (self.ip_last < other.ip_last):
            return -1
        elif (self.ip_last > other.ip_last):
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

# Parsing program starts here

if len(sys.argv) != 3:
    print("Usage: " + sys.argv[0] + " bgp_file + mapping_file")
    exit(1)

bgp_file = sys.argv[1]
nb_line = 0
nb_malformed = 0
nb_bad_prefix = 0
nb_sup_prefix = 0
nb_duplicates = 0
nb_parse_error = 0
nb_bad_line = 0
nb_ipv4 = 0
nb_ipv6 = 0

ipdom = dict()

try:
    for line in open(bgp_file , "rt"):
        try:
            nb_line += 1
            strip_line = line.strip()
            parts = strip_line.split(" ")
            prefix = parts[0]
            if prefix.startswith('>'):
                prefix_minus = prefix[1:]
                nb_sup_prefix += 1
                if nb_sup_prefix < 10:
                    print("Replaced prefix " + prefix + " by " + prefix_minus)
                prefix = prefix_minus
            prefix_parts = prefix.split("/")
            if len(parts) < 2:
                nb_malformed += 1
            elif len(prefix_parts) != 2:
                nb_bad_prefix += 1
                if nb_bad_prefix < 10:
                    print("Bad prefix: <" + strip_line + "> prefix: <" + prefix + "> prefix parts: " + str(len(prefix_parts))) 
            elif prefix in ipdom:
                nb_duplicates += 1
                ipdom[prefix].duplicates += 1
            else:
                ip_d_l = ipdom_line()
                try:
                    subnet = ipaddress.ip_network(prefix)
                    if subnet.version == 4:
                        nb_ipv4 += 1
                    else:
                        nb_ipv6 += 1
                    ip_d_l.ip_first = subnet.network_address
                    ip_d_l.ip_last = subnet.network_address + subnet.num_addresses - 1
                    if len(ipdom) < 10:
                        print(prefix + " = " + str(ip_d_l.ip_first) + " ... " + str(ip_d_l.ip_last))
                    if parts[len(parts)-1].startswith("{"):
                        ip_d_l.as_number = int(parts[len(parts)-2])
                    else:
                        ip_d_l.as_number = int(parts[len(parts)-1])
                    ipdom[prefix] = ip_d_l
                except Exception as e:
                    traceback.print_exc()
                    print("Got exception: " + str(e))
                    nb_parse_error += 1
                    if nb_parse_error < 10:
                        print("Bad line: <" + line.strip() + ">") 
        except Exception as e:
            traceback.print_exc()
            print("Got exception: " + str(e))
            nb_bad_line += 1
            if nb_bad_line < 10:
                print("Bad line: <" + line.strip() + ">") 
    print("Found " + str(nb_line) + " lines in " + bgp_file )
except:
    print("Error after " + str(nb_line) + " lines in " + bgp_file)

print("Entries: " + str(len(ipdom)))
print("IPv4: " + str(nb_ipv4))
print("IPv6: " + str(nb_ipv6))
print("Malformed: " + str(nb_malformed))
print("Bad_prefix: " + str(nb_bad_prefix))
print("Duplicates: " + str(nb_duplicates))
print("Parse_error: " + str(nb_parse_error))
print("Sup_prefix: " + str(nb_sup_prefix))
print("Bad_line: " + str(nb_parse_error))

prefix_list = []

for prefix in ipdom:
    prefix_list.append(ipdom[prefix])

print("List: " + str(len(prefix_list)))

sorted_list = sorted(prefix_list)

nb_item = 0

for item in sorted_list:
    nb_item += 1
    if nb_item < 100:
         print(str(item.ip_first) + "..." + str(item.ip_last))
    else:
        break

# TO DO: process the item list to eliminate overlaps
# TO DO: reduce the list by merging successive equivalent records
# TO DO: write reduced list to csv in first, last, ASN format -- becoming the default list
# TO DO: load as splay or similar, provide IP to ASN function.
