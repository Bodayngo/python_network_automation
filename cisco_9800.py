#!/usr/bin/env python3

"""
module docstring
"""

__author__ = "evan wilkerson"
__version__ = "beta-00.00.01"


import httpx
import json
from getpass import getpass


restconf_headers = {"Accept": "application/yang-data+json", "Content-Type": "application/yang-data+json",}


def get_APs(host, http_username, http_password):
    """ function docstring """
    with httpx.Client(verify=False, timeout=5.0) as client:
        response = client.get(
            url=f"https://{host}:443/restconf/data/Cisco-IOS-XE-wireless-access-point-oper:access-point-oper-data/capwap-data",
            params={"fields": "ip-addr;name;device-detail/static-info/board-data/wtp-enet-mac"},
            headers=restconf_headers,
            auth=(http_username, http_password)
        )
    if response.status_code == 200:
        access_points = json.loads(response.text)["Cisco-IOS-XE-wireless-access-point-oper:capwap-data"]
        return access_points
    print(response)
    return None


def filter_APs(aps):
    """ function docstring """
    while True:
        ap_filter = input(
            "enter in a partial or full ipv4 address to filter access points, "
            "or leave empty to target all access points"
            "\nfor example: '10.84', '10.84.40', or '10.84.40.25'\n> "  
        )
        filtered_aps = [ap for ap in aps if ap["ip-addr"].startswith(ap_filter)]
        if len(filtered_aps) != 0:
            for i in filtered_aps:
                print(f"{i['name']:<18} {i['ip-addr']:<18} {i['device-detail']['static-info']['board-data']['wtp-enet-mac']:<18}")
            user_confirm = input(f"{len(filtered_aps)} access points targeted with filter: '{ap_filter}'\nproceed? [y] ")
            if user_confirm.strip().lower() == 'y':
                return filtered_aps
        else:
            print(f"no access points found with filter: '{ap_filter}'")


def main():
    """ function docstring """
    host = input("enter in 9800 controller IPv4 address or FQDN\n> ")
    username = input("enter in 9800 controller HTTP/HTTPS username\n> ")
    password = getpass("enter in 9800 controller HTTP/HTTPS password\n> ")
    access_points = get_APs(host, username, password)
    if access_points:
        filtered_access_points = filter_APs(access_points)
        
    else:
        print("no access points.. exiting script")


if __name__ == "__main__":
    main()