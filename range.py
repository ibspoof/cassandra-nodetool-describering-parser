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
                    secondary_ranges.append({'ip': res.group(3).split(", ")[0], 'token_start': res.group(1), 'token_end': res.group(2)})
                found_cnt += 1

        CLUSTER_DETAILS[node]['range_cnt'] = found_cnt
        CLUSTER_DETAILS[node]['neighbors'] = secondary_ranges

    for dc in DATA_CENTERS:
        print "Datacenter: %s" % dc
        print ""
        for node in CLUSTER_DETAILS:
            if CLUSTER_DETAILS[node]['dc'] == dc:
                cur_node = CLUSTER_DETAILS[node]

                linked_nodes = []
                linked_ranges = []
                for n in cur_node['neighbors']:
                    linked_nodes.append(n['ip'])
                    linked_ranges.append("[%s, %s]" % (n['token_start'], n['token_end']))

                print "  %s" % node
                print "\t- Total Ranges: %s" % (cur_node['range_cnt'])
                print "\t- Primary Range: [%s, %s]" % (cur_node['token_start'], cur_node['token_end'])
                print "\t- Secondary Nodes: %s" % ", ".join(linked_nodes)
                print "\t- Secondary Ranges: %s" % ", ".join(linked_ranges)
                print ""
