import socket
import ipaddress
from concurrent.futures import ThreadPoolExecutor

def is_alive(ip):
    """Checks if ip is responding.

    :param ip: string - The IPv4 address that we are checking.
    :return: string or None - If port 80 is open on target ip it will return the ip
    for later storage, otherwise it will return None
    
    A function that utilizes the socket module to check if port 80 is responding 
    at the passed in IP.

    https://docs.python.org/3/library/socket.html#socket.socket.connect"""
    try:
        socket.setdefaulttimeout(1)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((str(ip), 80))
        return str(ip)
    except:
        return None

def scan_subnet(subnet):
    """Reports hosts that are responding on subnet.
    
    :param subnet: string - The subnet that is being scanned.
    :return: [strings] - A list of all the ips that responded on the subnet.
    
    A function that utilizes the is_alive() function to scan and build a list of
    all devices that are listening on port 80 on the provided subnet. Utilizes the
    ThreadPoolExecutor from the python standard library to run these checks concurrently.
    """
    network = ipaddress.ip_network(subnet, strict=False)
    print(f"scanning {subnet}...")

    # builds list of of responding hosts concurrently
    alive_hosts = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        results = executor.map(is_alive, network.hosts())
        for result in results:
            if result:
                print(f"host alive: {result}")
                alive_hosts.append(result)
    return alive_hosts

if __name__ == "__main__":
    subnet = "192.168.1.0/24"
    live = scan_subnet(subnet)
    print(f"discovered {len(live)} hosts.")