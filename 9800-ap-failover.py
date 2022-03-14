#!/usr/bin/env python3

"""
module docstring
"""

__author__ = "evan wilkerson"
__version__ = "beta-00.00.01"

import httpx
import json
import time
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
        "ipaddr": "10.5.40.11",
    },
    {
        "index": "index-tertiary",
        "controller-name": "TEST",
        "ipaddr": "192.168.255.1"
    },
]


def get_access_points(host, username, password):
    """
    function docstring
    """
    with httpx.Client(verify=False, timeout=5.0) as client:
        response = client.get(
            url=f"https://{host}:443/restconf/data/Cisco-IOS-XE-wireless-access-point-oper:"
            "access-point-oper-data/capwap-data",
            params={
                "fields": "ip-addr;name;device-detail/static-info/board-data/wtp-enet-mac"
            },
            headers=restconf_headers,
            auth=(username, password),
        )
    return response


def main():
    """
    function docstring
    """
    restconf_username = input("enter in controller HTTP/HTTPS username\n> ")
    restconf_password = getpass("enter in controller HTTP/HTTPS password\n> ")
    restconf_host = input("enter in controller FQDN or IPv4 address\n> ")
    start_time = time.time()
    print("getting access points...")
    access_points_response = get_access_points(
        restconf_host, restconf_username, restconf_password
    )
    if access_points_response.status_code == 200:
        access_points = json.loads(access_points_response.text)[
            "Cisco-IOS-XE-wireless-access-point-oper:capwap-data"
        ]
        print(f"{len(access_points)} access points found!\nconfiguring access points...")
        num_pass = 0
        num_fail = 0
        with httpx.Client(verify=False, timeout=5.0) as client:
            for access_point in access_points:
                controller_error = False
                for controller in controllers:
                    response = client.post(
                        url=f"https://{restconf_host}:443/restconf/data/" \
                            "Cisco-IOS-XE-wireless-access-point-cfg-rpc:set-ap-controller",
                        headers=restconf_headers,
                        auth=(restconf_username, restconf_password),
                        data=json.dumps(
                            {
                                "Cisco-IOS-XE-wireless-access-point-cfg-rpc:set-ap-controller": {
                                    "mode": "controller-name-enable",
                                    "controller-name": controller["controller-name"],
                                    "index": controller["index"],
                                    "ipaddr": controller["ipaddr"],
                                    "ap-name": access_point["name"],
                                }
                            }
                        ),
                    )
                    if response.status_code != 204:
                        controller_error = True
                if controller_error:
                    print(f"{access_point['name']} - failed")
                    num_fail += 1
                else:
                    print(f"{access_point['name']} - controllers configured")
                    num_pass += 1
        end_time = time.time()
        run_time = round((end_time - start_time), 2)
        print("completed!")
        print(f"{len(access_points)} access points configured in {run_time} seconds")
        print(f"succeeded={str(num_pass)}  failed:={str(num_fail)}")
    else:
        print(access_points_response)


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
