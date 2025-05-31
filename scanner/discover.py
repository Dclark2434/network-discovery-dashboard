import socket, ipaddress, subprocess, re
from concurrent.futures import ThreadPoolExecutor
from ports import TOP_100_TCP_PORTS

def is_alive(ip):
    """Checks if ip is responding.

    :param ip: string - The IPv4 address that we are checking.
    :return: string or None - If port 80 is open on target ip it will return the ip
    for later storage, otherwise it will return None
    
    A function that utilizes the socket module to check if port 80 is responding 
    at the passed in IP.

    https://docs.python.org/3/library/socket.html#socket.socket.connect"""

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            if s.connect_ex((str(ip), 80)) == 0:
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

def get_mac(ip):
    """Gets MAC address for device.
    
    :param ip: string - An ip address.
    :return: string - A mac address for the ip address passed in.
    
    A function that takes the passed in ip and looks up the MAC address using
    arp commands."""

    output = subprocess.check_output(("arp", "-a"))
    lines = output.splitlines()
    for line in lines:
        if ip in line:
            print("found matching ip in arp table")
            # below is the regex pattern for a mac address. it looks for 5
            # matches of pairs using the seen characters and then one more
            # match (total 6) of pairs all seperated by : or - you know...like a
            # mac address
            found = re.search("(([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2}))", line)
            if found: # returning .group() on None resulted in AttributeError
                return found.group()
    return None

def get_hostname(ip):
    """Gets hostname for device.
    
    :param ip: string - An ip address.
    :return: string - The hostname for the passed in ip address.
    
    A function that uses the socket modules reverse lookup feature to find and 
    return the hostname for the device with the provided ip. If none found it
    returns the original ip."""

    try:
        host_name = socket.gethostbyaddr(ip)[0]
        return host_name
    except socket.herror:
        return ip

# Is there a way to do this without nmap?
def get_os(ip):
    pass

def is_port_open(ip, port):
    """Checks if port is open.

    :param ip: string - ip we are checking
    :param port: int - port we are checking
    :return: Int or None - returns the port if open otherwise None
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            if s.connect_ex((str(ip), port)) == 0:
                return port
    except:
        return None

# if i do implement nmap usage in future this can be the fallback if unavailable
def get_open_ports(ip, ports=None):
    if ports is None:
        ports = TOP_100_TCP_PORTS
    open_ports = []
    with ThreadPoolExecutor(max_workers=50) as executor:
        results = executor.map(lambda port: is_port_open(ip, port), ports)
        for result in results:
            if result:
                print(f"Open Port: {result}")
                open_ports.append(result)
    return open_ports

def enrich_single_host(ip):
    host_data = {
    "ip": ip,
    "hostname": get_hostname(ip),
    "mac": get_mac(ip),
    "open_ports": get_open_ports(ip)
    }
    return host_data

def enrich_all_hosts(alive_hosts):
    for host in alive_hosts:
        enrich_single_host(host)

            
if __name__ == "__main__":
    subnet = "192.168.1.0/24"
    live = scan_subnet(subnet)
    print(f"discovered {len(live)} hosts.")