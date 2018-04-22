'''
APIC-EM Workshop
April 12, 2018
'''
import json
import requests
from tabulate import tabulate

# disable SSL certificate warnings
requests.packages.urllib3.disable_warnings()


class Node():
    """
    A generic class to store attributes for network hosts / devices.
    
    Example: 
        my_node = Node('wired', '192.168.0.2')

    Attributes (public):
        type (str): device type (or model for network devices)
        ip (str):   the ip address (or management address for network devices)
    """
    number = 0

    def __init__(self, dev_type=None, ip=None):
        self.type = dev_type
        self.ip = ip
        Node.number += 1

        # Keeps a count of all network devices / hosts
        self.number = Node.number

    def __str__(self):
        return('number: {}, type: {}, ip: {}'.format(
            self.number,
            self.type,
            self.ip
            )
        )


def get_ticket():
    """get_ticket: retrieves and returns a service ticket (token)
                   from the APIC-EM Sandbox"""
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
    # print("Ticket request status: ", resp.status_code)
    response_json = resp.json()
    serviceTicket = response_json["response"]["serviceTicket"]
    return serviceTicket


def get_session():
    """returns a session with default headers.
    Uses get_ticket to retrieve token"""
    ticket = get_ticket()
    session = requests.Session()
    session.headers['content-type'] = 'application/json'
    session.headers['X-Auth-Token'] = ticket

    return session


def get_hosts(session=None):
    '''
    get_hosts: returns an array of Node objects where each Node
    in the array stores data for a host
    '''
    api_url = "https://sandboxapicem.cisco.com/api/v1/host"

    if session is None:
        session = get_session()

    resp = session.get(api_url, verify=False)

    if resp.status_code != 200:
        raise Exception(
            "Status code does not equal 200. Response text: " + resp.text)
    response_json = resp.json()

    host_list = []
    for item in response_json["response"]:
        host_list.append(
            Node(item['hostType'],
                 item['hostIp']
                 )
            )
    return host_list


def print_nodes(data_function, session=None, caption=None):
    '''
    print_nodes: prints a table of nodes retrieved from fun with caption.
    '''
    table = []
    header = ["Number", "Type", "IP"]
    for n, data in enumerate(data_function(session)):
        table.append([n, data.type, data.ip])
    if caption:
        print('\n\n', caption, '\n')
    print(tabulate(table, header))


def get_devices(session=None):
    api_url = "https://sandboxapicem.cisco.com/api/v1/network-device"

    if session is None:
        session = get_session()
    resp = session.get(api_url, verify=False)

    if resp.status_code != 200:
        raise Exception(
            "Status code does not equal 200. Response text: " + resp.text)
    response_json = resp.json()

    device_list = []
    for item in response_json["response"]:
        device_list.append(
            Node(item['type'],
                 item['managementIpAddress']
                 )
            )
    return device_list
