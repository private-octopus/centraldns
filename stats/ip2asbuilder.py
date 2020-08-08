#!/usr/bin/python
# coding=utf-8
#
# Build an IP Address to AS number conversion table.
# The input should be the table ip2asn-v4.tsv from https://iptoasn.com/data/ip2asn-v4.tsv.gz

import sys
import traceback
import ipaddress

class ipdomv4_line:
    def __init__(self):
        self.as_number = 0
        self.duplicates = 0
        self.ip_first = ipaddress.ip_address("0.0.0.0")
        self.ip_last = ipaddress.ip_address("255.255.255.255")

    def compare(self, other):
        if (self.ip_first < other.ip_first):
            return -1
        elif (self.ip_first > other.ip_first):
            return 1
        elif (self.ip_last > other.ip_last):
            return -1
        elif (self.ip_last < other.ip_last):
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

def append_item_to_compact_list(item, compact_list, heap):
    ip_next = item.ip_last + 1
    if item.ip_first < ip_next:
        if len(compact_list) > 0 and \
           item.as_number == compact_list[len(compact_list) -1].as_number and \
           item.ip_first == compact_list[len(compact_list) -1].ip_last + 1:
           compact_list[len(compact_list) -1].ip_last = item.ip_last
        else:
           compact_list.append(item)
        i = 0
        while i < len(heap):
            heap[i].ip_first = ip_next
            i += 1


# Parsing program starts here

if len(sys.argv) != 3:
    print("Usage: " + sys.argv[0] + " ip2asn_file + mapping_file")
    exit(1)

ip2asn_file = sys.argv[1]
csv_file = sys.argv[2]
nb_line = 0
nb_duplicates = 0
nb_parse_error = 0
nb_bad_line = 0
nb_ipv4 = 0
nb_ipv6 = 0

ipdom = dict()

try:
    for line in open(ip2asn_file , "rt"):
        nb_line += 1
        strip_line = line.strip()
        parts = strip_line.split("\t")
        if len(parts) < 3:
            if nb_bad_line  < 10:
                printf("Malformed line: " + strip_line)
            nb_bad_line += 1
        else:
            ip_dv4 = ipdomv4_line()
            try:
                ip_dv4.ip_first = ipaddress.ip_address(parts[0])
                ip_dv4.ip_last = ipaddress.ip_address(parts[1])
                ip_dv4.as_number = int(parts[2])
                if len(ipdom) < 10:
                    print(str(ip_dv4.ip_first) + " ... " + str(ip_dv4.ip_last) + " --> " + str(ip_dv4.as_number))
                if ip_dv4.ip_first in ipdom:
                    if nb_duplicate < 10:
                        print("duplicate: " + str(ip_dv4.ip_first) + " ... " + str(ip_dv4.ip_last))
                    nb_duplicate += 1
                else:
                    ipdom[ip_dv4.ip_first] = ip_dv4          
            except Exception as e:
                traceback.print_exc()
                print("Got exception: " + str(e))
                nb_parse_error += 1
                if nb_parse_error < 10:
                    print("Parse error: <" + line.strip() + ">")
    print("Found " + str(nb_line) + " lines in " + ip2asn_file )
except:
    print("Error after " + str(nb_line) + " lines in " + ip2asn_file)

print("Entries: " + str(len(ipdom)))
print("Duplicates: " + str(nb_duplicates))
print("Parse_error: " + str(nb_parse_error))
print("Bad_line: " + str(nb_parse_error))

sorted_list = sorted(ipdom.values())

# save the result file

overlap_found = False
try:
    nb_saved = 0
    ip_previous = ipaddress.ip_address("0.0.0.0")
    after_first = False
    file_out = open(csv_file, "w")
    file_out.write("ip_first, ip_last, as_number,\n")
    for item in sorted_list :
        if after_first and item.ip_first <= ip_previous:
            print("Found overlap, " + str(item.ip_first) + "," + str(ip_previous))
            break
        ip_previous = item.ip_first
        after_first = True
        file_out.write(str(item.ip_first) + "," + str(item.ip_last) + "," + str(item.as_number) + ",\n")
        nb_saved += 1
    file_out.close()
    print("Saved " + str(nb_saved) + " ranges to " + csv_file)
except Exception as e:
    traceback.print_exc()
    print("Cannot write <" + csv_file+ ">, error: " + str(e));
