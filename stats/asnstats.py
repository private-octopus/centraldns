#!/usr/bin/python
# coding=utf-8
#
# This script extracts per ASN statictics from the results file.

import sys
import dns.resolver
import dnslook
import traceback
import ipaddress
import ip2as

class item_line:
    def __init__(self):
        self.count = 0
        self.asn = 0
   
    def compare(self, other):
        if (self.count > other.count):
            return -1
        elif (self.count < other.count):
            return 1
        if (self.asn < other.asn):
            return -1
        elif (self.asn > other.asn):
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

class count_bucket:
    def __init__(self):
        self.ip_count = 0
        self.number = 0

    def compare(self, other):
        if (self.ip_count < other.ip_count):
            return -1
        elif (self.ip_count > other.ip_count):
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


class count_item:
    def __init__(self):
        self.count = 0
        self.n_addr = 0
        self.n_domains = 0

    def compare(self, other):
        if (self.count > other.count):
            return -1
        elif (self.count < other.count):
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

class bucket_stats:
    def __init__(self):
        self.counts = dict()
        self.b_average = 0
        self.b_min = 0
        self.b_max = 0
        self.b_n_addr = 0
        self.b_nb_domains = 0

    def add(self, count):
        if count in self.counts:
            self.counts[count].number += 1
        else:
            item = count_bucket()
            item.ip_count = count
            item.number = 1
            self.counts[count] = item

    def do_stats(self):
        if len(self.counts) > 0:
           self.b_n_addr = 0
           self.b_average = 0
           self.b_min = 100000000000
           self.b_max = 0
           self.b_n_domains = 0
           for count in self.counts:
               self.b_n_domains += count * self.counts[count].number
               self.b_n_addr += self.counts[count].number
               self.b_min = min(self.b_min, count)
               self.b_max = max(self.b_max, count)
           self.b_average = self.b_n_domains / self.b_n_addr

class buckets:
    def __init__(self, asn_targets):
        self.overall = bucket_stats()
        self.other_asn = bucket_stats()
        self.asn_buckets = dict()
        for asn in asn_targets:
            self.asn_buckets[asn] = bucket_stats()

    def add(self, asn, count):
        if asn in self.asn_buckets:
            self.asn_buckets[asn].add(count)
        else:
            self.other_asn.add(count)
        self.overall.add(count)

    def do_stats(self):
        for asn in self.asn_buckets:
            self.asn_buckets[asn].do_stats()
        self.overall.do_stats()
        self.other_asn.do_stats()

#
# Main program, computation of statistics
#

if len(sys.argv) != 6:
    print("Usage: " + sys.argv[0] + " asnnames_file domain_list_file asn_stats_file ip_stats_file asn0_file")
    exit(1)

asnnames_file = sys.argv[1]
domain_list_file = sys.argv[2]
asn_stats_file = sys.argv[3]
ip_stats_file = sys.argv[4]
asn0_file = sys.argv[5]

asnamer = ip2as.asname()
if not asnamer.load(asnnames_file):
    print("Cannot load AS names from \"" + asnnames_file + "\"")
    exit(1)

asn_dict = dict()
ip_dict = dict()

nb_lines = 0
nb_domains = 0
nb_asn0 = 0
nb_asn_domains = 0

try:
    f_0 = open(asn0_file, "wt", encoding="utf-8")
    f_0.write("[\n")
    for line in open(domain_list_file , "rt"):
        nb_lines += 1 
        d = dnslook.dnslook()
        if d.from_json(line):
            nb_domains += 1
            if d.as_number == 0 or len(d.ip) == 0:
                if nb_asn0 > 0:
                    f_0.write(",\n")
                f_0.write(d.to_json())
                nb_asn0 += 1
            else:
                nb_asn_domains += 1
                if d.as_number in asn_dict:
                    asn_dict[d.as_number].count += 1
                else:
                    item = item_line()
                    item.asn = d.as_number
                    item.count = 1
                    asn_dict[d.as_number] = item
                ipa = d.ip[0]
                if ipa in ip_dict:
                    ip_dict[ipa].count += 1
                else:
                    item = item_line()
                    item.asn = d.as_number
                    item.count = 1
                    ip_dict[ipa] = item
    f_0.write("\n]\n")
    f_0.close()
    print("All done")
except Exception as e:
    traceback.print_exc()
    print("Cannot read file \"" + domain_list_file  + "\"\nException: " + str(e))
    print("Giving up");
    exit(1)


print("nb_lines: " + str(nb_lines))
print("nb_domains: " + str(nb_domains))
print("nb_asn0: " + str(nb_asn0))
print("nb_asn_domains: " + str(nb_asn_domains))
print("nb_asn: " + str(len(asn_dict)))
print("nb_ip: " + str(len(ip_dict)))

if nb_domains == 0:
    print("Did not find any domain in \"" + domain_list_file  + "\"")
    print("Giving up");
    exit(1)

asn_list = sorted(asn_dict.values())
c_cumul = 0
asn_top_number = 20
asn_top = []
asn_rank = 0
nb_written = 0
nb_total = 0

try:
    f_out = open(asn_stats_file, "wt", encoding="utf-8")
    f_out.write("ASN,Count,Cumul_C,Share,Cumul_S,ASName,ASCountry\n")
    for asnl in asn_list:
        if asn_rank < asn_top_number:
            asn_top.append(asnl.asn)
        asn_rank += 1
        share = asnl.count/nb_asn_domains
        c_cumul += asnl.count
        s_cumul = c_cumul/nb_asn_domains
        asname = asnamer.name(asnl.asn)
        asname_parts = asname.split(",")
        country = "??"
        astag = asname_parts[0].strip()
        i = 1
        while i < len(asname_parts) - 1:
            astag += " " + asname_parts[i].strip()
            i += 1
        if len(asname_parts) >= 2:
            country = asname_parts[-1].strip()
        f_out.write(str(asnl.asn) + "," + str(asnl.count) + "," + str(c_cumul) + "," + \
             str(100*share) + "%," + str(100*s_cumul) + "%," + \
             astag + "," + country + "\n")
        nb_written += 1
        nb_total += asnl.count
    f_out.close()
except Exception as e:
    traceback.print_exc()
    print("Cannot create file <" + asn_stats_file  + ">\nException: " + str(e))
    print("Giving up");
    exit(1)

print("nb_asn_written: " + str(nb_written))
print("nb_domains_counted: " + str(nb_total))

b = buckets(asn_top)
count_dict = dict()

n_max = 10
n_ip_print = 0

for item in ip_dict:
    if n_ip_print < n_max:
        print(str(item) + ", " + str(ip_dict[item].asn) + ", " + str(ip_dict[item].count))
        n_ip_print += 1
    b.add(ip_dict[item].asn, ip_dict[item].count)
    if ip_dict[item].count in count_dict:
        count_dict[ip_dict[item].count].n_addr += 1
        count_dict[ip_dict[item].count].n_domains += ip_dict[item].count
    else:
        x = count_item()
        x.count = ip_dict[item].count
        x.n_addr = 1
        x.n_domains = ip_dict[item].count
        count_dict[ip_dict[item].count] = x

b.do_stats()
count_list = sorted(count_dict.values())

for asn in b.asn_buckets:
    print(str(asn) + ": " + str(len(b.asn_buckets[asn].counts)) + " buckets.")

try:
    f_ip = open(ip_stats_file, "wt", encoding="utf-8")
    f_ip.write("ASN,n_domains,n_addr,n_average,n_min,n_max,ASName,ASCountry\n")
    for asn in b.asn_buckets:
        asname = asnamer.name(asn)
        asname_parts = asname.split(",")
        country = "??"
        astag = asname_parts[0].strip()
        i = 1
        while i < len(asname_parts) - 1:
            astag += " " + asname_parts[i].strip()
            i += 1
        if len(asname_parts) >= 2:
            country = asname_parts[-1].strip()
        x = b.asn_buckets[asn]
        f_ip.write(str(asn) + "," + str(x.b_n_domains) + "," + str(x.b_n_addr) + ","  \
            + str(x.b_average) + "," + str(x.b_min) + "," + str(x.b_max) + "," \
            + astag + "," + country +",\n")
    f_ip.write("," + str(b.other_asn.b_n_domains) + ","  + str(b.other_asn.b_n_addr) + "," + str(b.other_asn.b_average) + "," \
         + str(b.other_asn.b_min) + "," + str(b.other_asn.b_max) + ", all other ASes, ,\n")
    f_ip.write("," + str(b.overall.b_n_domains) + "," + str(b.overall.b_n_addr) + "," + str(b.overall.b_average) + "," \
         + str(b.overall.b_min) + "," + str(b.overall.b_max) + ", all included, ,\n")

    f_ip.write("\ncount, n_addr, n_domains\n")
    for c in count_list:
        f_ip.write(str(c.count) + "," + str(c.n_addr) + "," + str(c.n_domains) + "\n")
    f_ip.close()
except Exception as e:
    traceback.print_exc()
    print("Cannot create file <" + ip_stats_file  + ">\nException: " + str(e))
    print("Giving up");
    exit(1)

print("IP stats complete.")

b.do_stats()




exit(0)



f_out.close()
