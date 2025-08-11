#!/usr/bin/env python
import re
import sys

DATA_CENTERS = []
RANGE_SIZES = {}
REGEX_START_END_COMP = re.compile(r'.*TokenRange\(start_token:(.*), end_token:(.*), '
                                  r'endpoints:\[(.*)\], rpc_.* endpoint_details:\[(.*)]')
REGEX_ENDPNT_COMP = re.compile(r'EndpointDetails\(host:(.*), datacenter:(.*), rack:(.*)')
REGEX_STATUS_COMP = re.compile(r'^.* (\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b)\s(.*)\s([A-Za-z]+) (.*) .*')
REP_FACTOR = 3

if __name__ == """__main__""":

    nodetool_status_input = None

    if len(sys.argv) < 2:
        token_input = sys.stdin.read()
    else:
        token_input = open(sys.argv[1]).read()
        if len(sys.argv) > 2:
            nodetool_status_input = open(sys.argv[2]).read()

    CLUSTER_DETAILS = {}

    for line in token_input.split("\n"):

        if 'start_token' not in line:
            continue

        token_details = {}
        st_end_res = REGEX_START_END_COMP.match(line)

        token_details['token_start'] = st_end_res.group(1)
        token_details['token_end'] = st_end_res.group(2)
        token_details['ip'] = st_end_res.group(3).split(", ")[0]
        token_details['size'] = abs(int(token_details['token_end']) - int(token_details['token_start']))

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

    NODE_TOOL_STATUS = {}

    if nodetool_status_input is not None:
        for line in nodetool_status_input.split("\n"):
            res = REGEX_STATUS_COMP.match(line)
            if res is not None:
                NODE_TOOL_STATUS[res.group(1).strip()] = res.group(2).strip() + " " + res.group(3).strip()

    for dc in DATA_CENTERS:

        mean_range_size = round(sum(RANGE_SIZES[dc])) / max(len(RANGE_SIZES[dc]), 1)
        sorted_range = sorted(RANGE_SIZES[dc])
        smallest = sorted_range[0]
        largest = sorted_range[len(sorted_range) - 1]
        smallest_node = ""
        largest_node = ""

        print("Data Center: %s" % dc)
        print("")

        for node in CLUSTER_DETAILS:
            if CLUSTER_DETAILS[node]['dc'] == dc:
                cur_node = CLUSTER_DETAILS[node]

                if cur_node['size'] == smallest:
                    smallest_node = cur_node['ip']
                if cur_node['size'] == largest:
                    largest_node = cur_node['ip']

                linked_nodes = []
                linked_ranges = []
                linked_by_rack = {}
                for n in cur_node['neighbors']:
                    linked_nodes.append("%s" % n['ip'])
                    linked_ranges.append("%s: [%s, %s]" % (n['ip'], n['token_start'], n['token_end']))
                    if n['rack'] not in linked_by_rack:
                        linked_by_rack[n['rack']] = [n['ip']]
                    else:
                        linked_by_rack[n['rack']].append(n['ip'])

                print("  %s" % node)
                print("\tRack: %s" % cur_node['rack'])
                print("\tTotal Ranges: %s" % (cur_node['range_cnt']))
                if node in NODE_TOOL_STATUS:
                    print("\tData Size: %s" % NODE_TOOL_STATUS[node])
                print("\tPrimary: ")
                print("\t\tRange: [%s, %s]" % (cur_node['token_start'], cur_node['token_end']))
                print("\t\tRange Size: %s" % cur_node['size'])
                print("\t\t%% of Mean: %.2f" % (cur_node['size'] / mean_range_size))
                print("\tSecondary:")
                print("\t\tNodes: %s" % ", ".join(linked_nodes))
                print("\t\tRacks:")
                for r in linked_by_rack:
                    ips = ", ".join(linked_by_rack[r])
                    print("\t\t  - %s: %s" % (r, ips))
                print("\t\tRanges: ")
                for r in linked_ranges:
                    print("\t\t  - %s" % r)
                print("")

        print(" ")
        print("  Data Center Stats:")
        print("\tNode Count: %d" % len(RANGE_SIZES[dc]))
        print("\tMean Range Size:     %d" % mean_range_size)
        print("\tSmallest Range Size: %d\t\t(%s)" % (smallest, smallest_node))
        print("\tLargest Range Size:  %d\t(%s)" % (largest, largest_node))
