#!/usr/bin/env python3

"""
module docstring
"""

__author__ = "evan wilkerson"
__version__ = "beta-00.00.01"


import httpx
import json
from getpass import getpass


restconf_headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json",
}


def filter_access_points(aps):
    """
    function docstring
    """
    prompt = (
        "enter in a partial or full ipv4 address to filter access points, "
        "or leave empty to target all access points"
        "\nfor example: '10.84', '10.84.40', or '10.84.40.25'\n> "
    )
    while True:
        ap_filter = input(prompt)
        filtered_aps = [ap for ap in aps if ap["ip-addr"].startswith(ap_filter)]
        if len(filtered_aps) != 0:
            for i in filtered_aps:
                print(f"{i['name']:<18} {i['ip-addr']:<18} {i['device-detail']['static-info']['board-data']['wtp-enet-mac']:<18}")
            user_confirm = input(f"{len(filtered_aps)} access points targeted with filter: '{ap_filter}'\nproceed? [y] ")
            if user_confirm.strip().lower() == 'y':
                return filtered_aps
        print(f"no access points found with filter: '{ap_filter}'")


def main():
    """
    function docstring
    """
    host = '10.1.40.11' #input("enter in 9800 controller IPv4 address or FQDN\n> ")
    username = 'ejwilkerson' #input("enter in 9800 controller HTTP/HTTPS username\n> ")
    password = 'L0ck3r!291537' #getpass("enter in 9800 controller HTTP/HTTPS password\n> ")
    with httpx.Client(base_url=f"https://{host}:443/restconf/data", verify=False, timeout=5.0) as client:
        get_access_points_response = client.get(
            url="/Cisco-IOS-XE-wireless-access-point-oper:access-point-oper-data/capwap-data",
            params={"fields": "ip-addr;name;device-detail/static-info/board-data/wtp-enet-mac"},
            headers=restconf_headers,
            auth=(username, password)
        )
        if get_access_points_response.status_code == 200:
            access_points = json.loads(get_access_points_response.text)["Cisco-IOS-XE-wireless-access-point-oper:capwap-data"]
            filtered_access_points = filter_access_points(access_points)
            if filtered_access_points:
                for access_point in filtered_access_points:
                    print(access_point['name'])
        else:
            print("unable to get access points")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nuser has exited script")
    except RuntimeError:
        print("\nuser has exited script")
    except httpx.ConnectTimeout:
        print("timed out")
    except httpx.ConnectError:
        print("connection error")