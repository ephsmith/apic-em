"""
Path Trace Student Work File
APIC-EM Workshop
April 12, 2018
"""
import json
import time
from apic_em import get_ticket, get_hosts
from apic_em import get_devices, print_nodes, get_session
import re
import socket
from tabulate import tabulate
from graphviz import Digraph
import requests

# disable SSL certificate warnings
requests.packages.urllib3.disable_warnings()

headers = {
    "content-type": "application/json",
    "X-Auth-Token": get_ticket()
}


# Section 2.
# Display list of devices and IPs by calling get_host() and get_devices()
session = get_session()
print_nodes(get_hosts, session, caption='Host Table')
print_nodes(get_devices, session, caption='Device Table')
print("\n\n")

# Section 3. Get the source and destination IP addresses for the Path Trace

while True:

    s_ip = input("Enter the source IP: ")
    d_ip = input("Enter the destination IP: ")

    # validate ips
    err = False
    pat = re.compile('\.')
    if len(pat.findall(s_ip)) < 3 or len(pat.findall(d_ip)) < 3:
        err = True
    try:
        socket.inet_aton(s_ip)
        socket.inet_aton(d_ip)
    except:
        err = True

    if err:
        print('INVALID IPv4 ADDRESS ENTERED. Please try again')
        s_ip = None
        d_ip = None

    if s_ip and d_ip:
        path_data = {
            "sourceIP": s_ip,
            "destIP": d_ip
        }

        print('Using Source: {} and Dest: {}'.format(s_ip, d_ip))
        proceed = input('Proceed? (y/n): ')

        if proceed.upper() == 'Y':
            break  # Exit loop if values supplied
        else:
            s_ip = None
            d_ip = None
    else:
        print("\n\nYOU MUST ENTER IP ADDRESSES " +
              "TO CONTINUE.\nUSE CTRL-C TO QUIT\n")
        continue  # Return to beginning of loop and repeat

# Section 4. Initiate the Path Trace and get the flowAnalysisId

# Post request to initiate Path Trace
path = json.dumps(path_data)
api_url = "https://sandboxapicem.cisco.com/api/v1/flow-analysis"
# resp = requests.post(api_url, path, headers=headers, verify=False)
resp = session.post(api_url, path, verify=False)

# Inspect the return, get the Flow Analysis ID, put it into a variable
resp_json = resp.json()
flowAnalysisId = resp_json["response"]['flowAnalysisId']
print("FLOW ANALYSIS ID: ", flowAnalysisId)

# begin checking status of request
check_url = api_url + "/" + flowAnalysisId

# initialize variable to hold the status of the path trace
status = ""
checks = 1  # Will trigger exit from loop after x iterations

while status != "COMPLETED":
    r = session.get(check_url, verify=False)
    response_json = r.json()
    time.sleep(1)
    status = response_json["response"]["request"]['status']

    print("REQUEST STATUS: ", status)  # Print the status as the loop runs

    if checks == 15:
        # break the execution
        raise Exception(
            "Number of status checks exceeds limit." +
            "Possible problem with Path Trace.!"
        )
    elif status == "FAILED":
        # break the execution
        raise Exception("Problem with Path Trace - FAILED!")
    checks += 1


# Section 6. Display results
path_source = response_json["response"]["request"]["sourceIP"]
path_dest = response_json["response"]['request']['destIP']
networkElementsInfo = response_json["response"]['networkElementsInfo']

all_devices = []
device_no = 1

# Iterate through returned Path Trace JSON and populate list of path
# information
for networkElement in networkElementsInfo:

    if "name" not in networkElement:
        name = "Unnamed Host"
        ip = networkElement["ip"]
        egressInterfaceName = "UNKNOWN"
        ingressInterfaceName = "UNKNOWN"
    else:
        name = networkElement["name"]
        ip = networkElement["ip"]
        if "egressInterface" in networkElement:
            egressInterfaceName = (networkElement["egressInterface"]
                                   ["physicalInterface"]
                                   ["name"])
        else:
            egressInterfaceName = "UNKNOWN"

        if "ingressInterface" in networkElement:
            ingressInterfaceName = (networkElement["ingressInterface"]
                                    ["physicalInterface"]
                                    ["name"])
        else:
            ingressInterfaceName = "UNKNOWN"

    # create the list of info to be displayed
    device = [
                device_no,
                name,
                ip,
                ingressInterfaceName,
                egressInterfaceName
             ]
    all_devices.append(device)
    device_no += 1

# print the source and destination IPs for the trace
print("Path trace: \n Source: ",
      path_source,
      "\n Destination: ",
      path_dest)

# print the table of devices in the path trace
print("List of devices on path:")
table_header = [
                "Item",
                "Name",
                "IP",
                "Ingress Int",
                "Egress Int"
               ]
print(tabulate(all_devices, table_header))

graph = Digraph('Path Trace')

for n, dev in enumerate(all_devices):
    graph.node(str(n), dev[1])

    if n > 0:
        last_dev = all_devices[n-1]
        graph.edge(str(n-1), str(n),
                   label='{}->{}'.format(last_dev[2], dev[2]))
print('\n\ngraphviz output\n')
print(graph.source)
