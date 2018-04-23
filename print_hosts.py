"""
APIC-EM Workshop
April 12, 2018
"""

import requests
from tabulate import tabulate
from apic_em import get_hosts

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()  


def print_hosts():
    """Prints a table of hosts. NOTE: This calls apic_em.get_hosts
       for the list of hosts.
    """
    host_list = []
    for n, host in enumerate(get_hosts()):
        host_list.append(
            [n,
             host.type,
             host.ip
             ])
    table_header = ["Number", "Type", "IP"]
    print(tabulate(host_list, table_header))


print_hosts()
