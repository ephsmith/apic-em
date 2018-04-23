import requests
from apic_em import get_devices
from tabulate import tabulate

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()


def print_devices():
    """Prints network devices and IP addresses. Note, uses get_devices
    """
    device_table = []
    for n, device in enumerate(get_devices()):
        device_table.append(
            [n,
             device.type,
             device.ip
             ])
    table_header = ["Number", "Type", "Management IP"]
    print(tabulate(device_table, table_header))


print_devices()
