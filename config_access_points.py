#!/usr/bin/env python3

"""
module docstring
"""

__author__ = "evan wilkerson"
__version__ = "beta-00.00.01"


from getpass import getpass
import json
import httpx


restconf_headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json",
}


def get_store_initials(store_number):
    """
    function docstring
    """
    stores = {
        6: "DS",
        16: "SH",
        20: "MO",
        22: "CS",
        24: "MI",
        40: "EA",
        44: "IC",
        48: "SF",
        50: "SM",
        54: "AP",
        56: "SC",
        58: "OM",
        60: "DM",
        62: "RH",
        64: "FA",
        70: "GF",
        72: "KI",
        74: "RS",
        76: "RC",
        78: "SP",
        80: "SS",
        82: "CF",
        84: "GK",
        86: "BL",
        88: "OP",
        90: "RO",
        92: "JO",
        94: "LI",
        96: "TC",
        98: "EN",
        110: "WH_FA",
        144: "WH_IC",
        252: "CO",
    }
    return stores[int(store_number)]


def get_access_points(host, http_username, http_password):
    """function docstring"""
    with httpx.Client(verify=False, timeout=5.0) as client:
        response = client.get(
            url=f"https://{host}:443/restconf/data/" \
                "Cisco-IOS-XE-wireless-access-point-oper:access-point-oper-data/capwap-data",
            params={
                "fields": "ip-addr;name;device-detail/static-info/board-data/wtp-enet-mac"
            },
            headers=restconf_headers,
            auth=(http_username, http_password),
        )
    if response.status_code == 200:
        access_points = json.loads(response.text)[
            "Cisco-IOS-XE-wireless-access-point-oper:capwap-data"
        ]
        return access_points
    print(response)
    return None


def filter_access_points(aps):
    """function docstring"""
    while True:
        ap_filter = input(
            "enter in partial/full IPv4 address to filter APs or leave empty to target all APs"
            "\n('10.84' or '10.84.40' or '10.84.40.125')"
            "\n> "
        )
        filtered_aps = [ap for ap in aps if ap["ip-addr"].startswith(ap_filter)]
        if len(filtered_aps) != 0:
            print(f"{len(filtered_aps)} access points targeted with filter: '{ap_filter}'")
            user_confirm = input("proceed? [y] ")
            if user_confirm.strip().lower() == "y":
                return filtered_aps
        else:
            print(f"no access points found with filter: '{ap_filter}'")


def factory_reset_access_points(host, username, password, access_points):
    """
    function docstring
    """
    with httpx.Client(
        base_url=f"https://{host}:443/restconf/data", verify=False, timeout=5.0
    ) as client:
        for access_point in access_points:
            data = {
                "Cisco-IOS-XE-wireless-access-point-cmd-rpc:clear-ap-config": {
                    "operation-type": "ap-clear-config",
                    "ap-name": f"{access_point['name']}",
                }
            }
            response = client.post(
                url="/Cisco-IOS-XE-wireless-access-point-cmd-rpc:clear-ap-config",
                headers=restconf_headers,
                auth=(username, password),
                data=json.dumps(data),
            )
            print(f"{access_point['name']} - clear config - {response}")


def config_access_point_names(host, username, password, access_points):
    """function docstring"""
    with httpx.Client(
        base_url=f"https://{host}:443/restconf/data", verify=False, timeout=5.0
    ) as client:
        for access_point in access_points:
            store_initials = get_store_initials(
                int(access_point["ip-addr"].split(".")[1])
            )
            mac = access_point['device-detail']['static-info']['board-data']['wtp-enet-mac']
            old_name = access_point["name"]
            new_name = f"{store_initials}-{mac.replace(':', '').upper()}"
            if old_name == new_name:
                print(f"{access_point['name']} - configure name - skipped")
            else:
                data = {
                    "Cisco-IOS-XE-wireless-access-point-cfg-rpc:set-ap-name": {
                        "name": new_name,
                        "ap-name": old_name,
                    }
                }
                response = client.post(
                    url="/Cisco-IOS-XE-wireless-access-point-cfg-rpc:set-ap-name",
                    headers=restconf_headers,
                    auth=(username, password),
                    data=json.dumps(data),
                )
                print(f"{access_point['name']} - configure name - {response}")


def config_access_point_controllers(host, username, password, access_points):
    """function docstring"""
    with httpx.Client(
        base_url=f"https://{host}:443/restconf/data", verify=False, timeout=5.0
    ) as client:
        for access_point in access_points:
            controllers = [
                {
                    "index": "index-primary",
                    "controller-name": "D1-9800-1",
                    "ipaddr": "10.1.40.11",
                },
                {
                    "index": "index-secondary",
                    "controller-name": "D2-9800-1",
                    "ipaddr": "10.5.40.11",
                },
            ]
            for controller in controllers:
                data = {
                    "Cisco-IOS-XE-wireless-access-point-cfg-rpc:set-ap-controller": {
                        "mode": "controller-name-enable",
                        "controller-name": controller["controller-name"],
                        "index": controller["index"],
                        "ipaddr": controller["ipaddr"],
                        "ap-name": access_point["name"],
                    }
                }
                response = client.post(
                    url="Cisco-IOS-XE-wireless-access-point-cfg-rpc:set-ap-controller",
                    headers=restconf_headers,
                    auth=(username, password),
                    data=json.dumps(data),
                )
                print(
                    f"{access_point['name']} - {controller['index']} - {response}"
                )


def config_access_point_tags(username, password, access_points):
    """function docstring"""
    tag_config = {"Cisco-IOS-XE-wireless-ap-cfg:ap-tags": {"ap-tag": []}}
    for access_point in access_points:
        store_initials = get_store_initials(int(access_point["ip-addr"].split(".")[1]))
        ap_mac = access_point["device-detail"]["static-info"]["board-data"][
            "wtp-enet-mac"
        ]
        tag_config["Cisco-IOS-XE-wireless-ap-cfg:ap-tags"]["ap-tag"].append(
            {
                "ap-mac": ap_mac,
                "policy-tag": f"{store_initials}_Policy_Tag",
                "site-tag": f"{store_initials}_Site_Tag",
                "rf-tag": "RF_Tag",
            }
        )
    data = json.dumps(tag_config)
    controllers = ["d1-9800-1.net.scheelssports.pvt", "d2-9800-1.net.scheelssports.pvt"]
    with httpx.Client(verify=False, timeout=5.0) as client:
        for controller in controllers:
            response = client.patch(
                url=f"https://{controller}:443/restconf/data/" \
                    "Cisco-IOS-XE-wireless-ap-cfg:ap-cfg-data/ap-tags",
                headers=restconf_headers,
                auth=(username, password),
                data=data,
            )
            print(f"{controller} - {response}")


def main():
    """function docstring"""
    host = input("enter in 9800 controller IPv4 address or FQDN\n> ")
    username = input("enter in 9800 controller HTTP/HTTPS username\n> ")
    password = getpass("enter in 9800 controller HTTP/HTTPS password\n> ")
    access_points = get_access_points(host, username, password)
    if access_points:
        filtered_access_points = filter_access_points(access_points)
        while True:
            config_menu_input = int(input("""select access point configuration option below:
  [0]  clear access point config (factory reset)
  [1]  configure access point names
  [2]  configure access point controllers
  [3]  configure access point tags
> """).strip())
            if config_menu_input == 0:
                factory_reset_access_points(host, username, password, filtered_access_points)
                break
            if config_menu_input == 1:
                config_access_point_names(host, username, password, filtered_access_points)
                break
            if config_menu_input == 2:
                config_access_point_controllers(host, username, password, filtered_access_points)
                break
            if config_menu_input == 3:
                config_access_point_tags(username, password, access_points)
                break
            print("invalid option")
    else:
        print("no access points.. exiting script")


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
