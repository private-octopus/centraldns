#!/usr/bin/python
# coding=utf-8
#
# The look1million script takes as input a list of domain names such as Cisco Umbrella 1M
# (https://umbrella.cisco.com/blog/cisco-umbrella-1-million) or the Majestic Million
# (https://majestic.com/reports/majestic-million). These lists come in different
# formats. We assume here that the original input is preprocessed to produce a text
# file with one domain per line, ranked from most popular to least popular.
#
# The program will read the million name file and for each name preform a dns lookup,
# gathering properties like IP addresses, NS records and the chain of CNAME records.
# Once a name is looked up, the corresponding JSON entry is appended to the "domainlist"
# file. This text file contains one line per domain, encoded as a JSON string, as produced
# by the dnslook object.
#
# The program has a simple strategy: process the names in order, from start to finish.
# When the program starts, it reads the current content of the domainlist file and builds
# a dictionary of the names that are already processed. Then it reads the million names
# file in order, and tries to document any name that is not already processed. The idea
# is that the program may be interrupted before finishing, and thus needs to be able to
# stop and restart without duplicating work.
#
# For testing purpose, the program takes an optional argument specifying the number of 
# names that it wants to process in one batch. If that argument is present, the program stops
# after processing the specified amount.
# 

import sys
import traceback
import dnslook
import os.path
import publicsuffix
import ip2as

def usage(sn):
    print("Usage: " + sn + " ip2as.csv publicsuffix.dat million_file domain_list_file [nb_search]")
    exit(1)

# Check the input arguments

if len(sys.argv) < 5 or len(sys.argv) > 6:
    usage(sys.argv[0])
ip2as_file = sys.argv[1]
public_suffix_file = sys.argv[2]
million_file = sys.argv[3]
domain_list_file = sys.argv[4]
nb_to_search = 1000000
if len(sys.argv) == 6:
    try:
        nb_to_search = int(sys.argv[5])
    except:
        print(sys.argv[5] + " is not a valid number.")
        usage(sys.argv[0])

# create the tables of public suffix and as number 
ps = publicsuffix.public_suffix()
if not ps.load_file(public_suffix_file):
    print("Could not load the suffixes")
    exit(1)

i2a = ip2as.ip2as_table()
if i2a.load(ip2as_file):
    print("Loaded i2a table of length: " + str(len(i2a.table)))
else:
    print("Could not load <" + ip2as_file + ">")
    exit(1)

# create the dictionary of names.
domains = dict()

# if domainlist file exists, try to read it.
nb_domains = 0
nb_lines = 0
if os.path.isfile(domain_list_file):
    try: 
        for line in open(domain_list_file , "rt"):
            nb_lines += 1 
            domain = dnslook.dnslook()
            if domain.from_json(line):
                domains[domain.domain] = domain
                nb_domains += 1
    except Exception as e:
        traceback.print_exc()
        print("Cannot read file <" + domain_list_file  + ">\nException: " + str(e))
        print("Giving up");
        exit(1)
    if nb_lines > 0 and nb_domains == 0:
        print("Nothing to read in file <" + domain_list_file  + ">\nGiving up.")
        exit(1)
    
# try to process the million names list.
try:
    f_out = open(domain_list_file, "at")
except Exception as e:
    traceback.print_exc()
    print("Cannot open domain list file <" + domain_list_file  + ">\nException: " + str(e))
    print("Giving up");
    exit(1)

try:
    f_in = open(million_file , "rt")
except Exception as e:
    traceback.print_exc()
    print("Cannot open million file <" + million_file  + ">\nException: " + str(e))
    print("Giving up");
    f_out.close()
    exit(1)

nb_domains_added = 0
nb_domains_searched = 0
try:
    for line in f_in:
        name = line.strip()
        if not name in domains:
            nb_domains_searched += 1
            domain = dnslook.dnslook()
            domain.get_domain_data(line.strip(), ps, i2a)
            f_out.write(domain.to_json() + "\n")
            domains[domain.domain] = domain
            nb_domains_added += 1
            if nb_domains_searched >= nb_to_search:
                break
except Exception as e:
    traceback.print_exc()
    print("Cannot search new domain\nException: " + str(e))
    print("Giving up");
f_in.close()
f_out.close()
print("Searched domains: " + str(nb_domains_searched))
print("Added domains: " + str(nb_domains_added))
print("Total domains: " + str(len(domains)))