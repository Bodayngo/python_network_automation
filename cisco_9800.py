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


def get_access_points(host, http_username, http_password):
    """ function docstring """
    with httpx.Client(verify=False, timeout=5.0) as client:
        response = client.get(
            url=f"https://{host}:443/restconf/data/Cisco-IOS-XE-wireless-access-point-cmd-rpc:clear-ap-config",
            params={"fields": "ip-addr;name;device-detail/static-info/board-data/wtp-enet-mac"},
            headers=restconf_headers,
            auth=(http_username, http_password)
        )