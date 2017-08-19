#!/usr/bin/env python
import re
import sys

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

DATA_CENTERS = []
RANGE_SIZES = {}
REGEX_START_END_COMP = re.compile(r'.*TokenRange\(start_token:(.*), end_token:(.*), '
                                  r'endpoints:\[(.*)\], rpc_.* endpoint_details:\[(.*)]')
REGEX_ENDPNT_COMP = re.compile(r'EndpointDetails\(host:(.*), datacenter:(.*), rack:(.*)')
REP_FACTOR = 3

if __name__ == """__main__""":

    if len(sys.argv) < 2:
        token_input = sys.stdin.read()
    else:
        token_input = open(sys.argv[1]).read()

    CLUSTER_DETAILS = {}

    for line in token_input.split("\n"):

        if 'start_token' not in line:
            continue

        token_details = {}
        st_end_res = REGEX_START_END_COMP.match(line)

        token_details['token_start'] = st_end_res.group(1)
        token_details['token_end'] = st_end_res.group(2)
        token_details['ip'] = st_end_res.group(3).split(", ")[0]
        token_details['size'] = abs(long(token_details['token_end']) - long(token_details['token_start']))

        replicas = st_end_res.group(4)

        replica_info = []
        rep_cnt = 0
        for rep in replicas.split("), "):
            res = REGEX_ENDPNT_COMP.match(rep)
            if rep_cnt is 0:
                token_details['dc'] = res.group(2)
                token_details['rack'] = res.group(3)
            else:
                replica_info.append({'ip': res.group(1), 'dc': res.group(2), 'rack': res.group(3)})
            rep_cnt += 1

        token_details['replicas'] = replica_info

        if token_details['dc'] not in RANGE_SIZES:
            RANGE_SIZES[token_details['dc']] = [token_details['size']]
        else:
            RANGE_SIZES[token_details['dc']].append(token_details['size'])

        if token_details['dc'] not in DATA_CENTERS:
            DATA_CENTERS.append(token_details['dc'])


        CLUSTER_DETAILS[token_details['ip']] = token_details

    for node in CLUSTER_DETAILS:
        secondary_ranges = []
        found_cnt = 0
        for line in token_input.split("\n"):
            res = REGEX_START_END_COMP.match(line)
            if line.find(node + ",") > -1:
                if res.group(3).split(", ")[0] != CLUSTER_DETAILS[node]['ip']:
                    secondary_rep = {'ip': res.group(3).split(", ")[0], 'token_start': res.group(1),
                                     'token_end': res.group(2)}
                    secondary_rep['rack'] = CLUSTER_DETAILS[secondary_rep['ip']]['rack']
                    secondary_ranges.append(secondary_rep)
                found_cnt += 1

        CLUSTER_DETAILS[node]['range_cnt'] = found_cnt
        CLUSTER_DETAILS[node]['neighbors'] = secondary_ranges

    for dc in DATA_CENTERS:


        # avg_range_size = sum(RANGE_SIZES[dc]) / len(RANGE_SIZES[dc])
        avg_range_size = float(sum(RANGE_SIZES[dc])) / max(len(RANGE_SIZES[dc]), 1)
        sorted_range = sorted(RANGE_SIZES[dc])
        smallest = sorted_range[0]
        largest = sorted_range[len(sorted_range) - 1]

        print "Datacenter: %s" % dc
        print ""

        for node in CLUSTER_DETAILS:
            if CLUSTER_DETAILS[node]['dc'] == dc:
                cur_node = CLUSTER_DETAILS[node]

                linked_nodes = []
                linked_ranges = []
                for n in cur_node['neighbors']:
                    linked_nodes.append("%s (%s)" % (n['ip'], n['rack']))
                    linked_ranges.append("%s: [%s, %s]" % (n['ip'], n['token_start'], n['token_end']))

                diff_percent = abs((float(cur_node['size'] - float(avg_range_size))) / float(avg_range_size)) * 100.0

                print "  %s" % node
                print "\t- Total Ranges: %s" % (cur_node['range_cnt'])
                print "\t- Primary Range: [%s, %s]" % (cur_node['token_start'], cur_node['token_end'])
                print "\t- Primary Range Size: %s    (Diff from avg: %d%%)" % (cur_node['size'], diff_percent)
                print "\t- Secondary Nodes: %s" % ", ".join(linked_nodes)
                print "\t- Secondary Ranges: "
                for r in linked_ranges:
                    print "\t\t%s" % r
                print ""

        print "  Token range sizes:"
        print "\tSmallest: %d" % smallest
        print "\tLargest: %d" % largest
        print "\tAverage: %d" % avg_range_size

