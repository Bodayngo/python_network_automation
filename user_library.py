#!/usr/bin/env python3

"""
module docstring
"""

__author__ = "evan wilkerson"
__version__ = "beta-00.00.01"

from getpass import getpass
import ipaddress


def get_username(username_prompt="enter in username\n> "):
    """
    Description
        Gets username from user cli input
    Parameters
        username_prompt (str) optional: The prompt displayed for username input
    Returns
        username (str): A username to be used for authentication
    """
    while True:
        username = str(input(username_prompt))
        if int(len(username)) != 0:
            return username
        print("*** username input cannot be empty")


def get_password(password_prompt="enter in password\n> "):
    """
    Description
        Gets password from user cli input
    Parameters
        password_prompt (str) optional: The prompt displayed for password input
    Returns
        password (str): A password to be used for authentication
    """
    while True:
        password = str(getpass(password_prompt))
        if int(len(password)) != 0:
            return password
        print("*** password input cannot be empty")


def get_ipv4_address(ipv4_address_prompt="enter in an ipv4 address (x.x.x.x)\n> "):
    """
    Description
        Gets host IPv4 address from user cli input
    Parameters
        ipv4_address_prompt (str) optional: The prompt displayed for IPv4 address input
    Returns
        host_ipv4_address (str): A valid IPv4 address
    """
    while True:
        host_ipv4_address = input(ipv4_address_prompt)
        try:
            ipaddress.ip_address(host_ipv4_address)
        except ValueError:
            print("*** invalid ip address")
            continue
        else:
            return host_ipv4_address
