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
controllers = [
    {
        "index": "index-primary",
        "controller-name": "D1-9800-1",
        "ipaddr": "10.1.40.11"
    },
    {
        "index": "index-secondary",
        "controller-name": "D2-9800-1",
        "ipaddr": "10.5.40.11"
    },
    {
        "index": "index-tertiary",
        "controller-name": "TEST",
        "ipaddr": "192.168.255.1"
    }
]


def get_access_points(host, uname, passwd):
    """
    function docstring
    """
    print("getting access points...")
    with httpx.Client(verify=False, timeout=5.0) as c:
        r = c.get(
            url=f"https://{host}:443/restconf/data/Cisco-IOS-XE-wireless-access-point-oper:" \
                "access-point-oper-data/capwap-data",
            params={
                "fields": "ip-addr;name;device-detail/static-info/board-data/wtp-enet-mac"
            },
            headers=restconf_headers,
            auth=(uname, passwd)
        )
    if r.status_code == 200:
        aps = json.loads(r.text)["Cisco-IOS-XE-wireless-access-point-oper:capwap-data"]
        print(f"{len(aps)} access points found!")
        return aps
    print(f"unable to get access points: {r}")
    return None


def filter_access_points(aps):
    """
    function docstring
    """
    prompt = (
        "enter in a partial or full ipv4 address to filter access points, "
        "or leave empty to target all access points"
        "\nfor example: '10.84', '10.84.40', or '10.84.40.25'\n> "
    )
    ap_filter = input(prompt)
    filtered_aps = [ap for ap in aps if ap["ip-addr"].startswith(ap_filter)]
    if len(filtered_aps) != 0:
        return filtered_aps
    print(f"no access points found with filter: '{ap_filter}'")
    return None


def main():
    """
    function docstring
    """
    r_uname = input("enter in controller HTTP/HTTPS username\n> ")
    r_passwd = getpass("enter in controller HTTP/HTTPS password\n> ")
    r_host = input("enter in controller FQDN or IPv4 address\n> ")
    aps = get_access_points(r_host, r_uname, r_passwd)
    if aps:
        filtered_aps = filter_access_points(aps)
        if filtered_aps:
            for ap in filtered_aps:
                print(f"{ap['name']:<18} {ap['ip-addr']:<18}")


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
