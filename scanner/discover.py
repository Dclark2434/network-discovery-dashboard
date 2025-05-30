import socket
import ipaddress
from concurrent.futures import ThreadPoolExcecutor

def is_alive(ip):
    pass

def scan_subnet(subnet):
    pass

if __name__ == "__main__":
    subnet = "192.168.1.0/24"
    live = scan_subnet(subnet)
    print(f"discovered {len(live)} hosts.")