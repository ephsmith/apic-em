"""
APIC-EM Workshop
April 12, 2018
"""

import requests
import json
from tabulate import tabulate

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()  


def get_ticket():
    '''
    get_ticket: retrieves and returns a service ticket (token)
                from the APIC-EM Sandbox
    '''
    main_api = "https://sandboxapicem.cisco.com/api/v1/ticket"
    headers = {"content-type": "application/json"}
    body_json = {
        "username": "devnetuser",
        "password": "Cisco123!",
    }
    resp = requests.post(main_api,
                         json.dumps(body_json),
                         headers=headers,
                         verify=False)
    print("Ticket request status: ", resp.status_code)
    response_json = resp.json()
    serviceTicket = response_json["response"]["serviceTicket"]
    return serviceTicket


def print_hosts():
    api_url = "https://sandboxapicem.cisco.com/api/v1/host"
    ticket = get_ticket()
    headers = {
        "content-type": "application/json",
        "X-Auth-Token": ticket
    }
    
    resp = requests.get(api_url, headers=headers, verify=False)
    print("Status of /host request: ", resp.status_code)
    if resp.status_code != 200:
        raise Exception(
            "Status code does not equal 200. Response text: " + resp.text)
    response_json = resp.json()
    
    host_list = []
    i = 0
    for item in response_json["response"]:
        i += 1
        host = [
            i,
            item["hostType"],
            item["hostIp"]
        ]
        host_list.append(host)
        table_header = ["Number", "Type", "IP"]
    print(tabulate(host_list, table_header))


print_hosts()
