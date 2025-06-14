import socket
import ipaddress
import subprocess
import re
import platform
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from scanner.ports import TOP_100_TCP_PORTS

def is_alive(ip):
    """Check if the given host responds to a ping request.

    Parameters
    ----------
    ip : str
        The IPv4 address to probe.

    Returns
    -------
    str or None
        Returns the IP address if the host responds, otherwise ``None``.

    The previous implementation attempted to connect to a handful of common
    TCP ports. While that works for many devices, it can miss hosts with all of
    those ports closed. Performing a small ICMP ping is much faster and gives a
    better view of all hosts on the subnet.
    """

    system = platform.system().lower()
    if system == "windows":
        cmd = ["ping", "-n", "1", "-w", "1000", str(ip)]
    else:
        cmd = ["ping", "-c", "1", "-W", "1", str(ip)]

    try:
        result = subprocess.run(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        if result.returncode == 0:
            return str(ip)
    except Exception:
        pass
    return None

def scan_subnet(subnet):
    """Reports hosts that are responding on subnet.
    
    :param subnet: string - The subnet that is being scanned.
    :return: [strings] - A list of all the ips that responded on the subnet.
    
    A function that utilizes the :func:`is_alive` function to scan and build a
    list of all devices that respond to a ping on the provided subnet. It uses
    :class:`ThreadPoolExecutor` from the Python standard library to run these
    checks concurrently.
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

def _get_mac_from_arp(ip):
    """Gets MAC address for device.
    
    :param ip: string - An ip address.
    :return: string - A mac address for the ip address passed in.
    
    A function that takes the passed in ip and looks up the MAC address using
    arp commands."""

    output = subprocess.check_output(("arp", "-a")).decode()
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

@lru_cache(maxsize=None)
def get_os_and_mac(ip):
    """Run nmap to obtain OS and MAC address information."""
    try:
        output = subprocess.check_output(["nmap", "-O", "-n", ip], stderr=subprocess.STDOUT, timeout=30).decode()
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return None, None
    os_name = None
    mac = None
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("OS details:"):
            os_name = line.split("OS details:")[1].strip()
        if "MAC Address:" in line:
            m = re.search(r"([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}", line)
            if m:
                mac = m.group(0)
    return os_name, mac

def get_os(ip):
    os_name, _ = get_os_and_mac(ip)
    return os_name


def get_mac(ip):
    _, mac = get_os_and_mac(ip)
    if mac:
        return mac
    return _get_mac_from_arp(ip)

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
    """Return list of open ports using nmap when available.

    Falls back to a basic socket scan if nmap cannot be executed.
    """
    if ports is None:
        ports = TOP_100_TCP_PORTS

    port_list = ','.join(str(p) for p in ports)
    try:
        output = subprocess.check_output(
            ["nmap", "-p", port_list, "--open", "-n", ip],
            stderr=subprocess.STDOUT,
            timeout=30,
        ).decode()
        open_ports = []
        for line in output.splitlines():
            line = line.strip()
            m = re.match(r"(\d+)/tcp\s+open", line)
            if m:
                open_ports.append(int(m.group(1)))
        return open_ports
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        open_ports = []
        with ThreadPoolExecutor(max_workers=50) as executor:
            results = executor.map(lambda port: is_port_open(ip, port), ports)
            for result in results:
                if result:
                    open_ports.append(result)
        return open_ports

def enrich_single_host(ip):
    host_data = {
        "ip": ip,
        "hostname": get_hostname(ip),
        "mac": get_mac(ip),
        "os": get_os(ip),
        "open_ports": get_open_ports(ip)
    }
    return host_data

# finally lets put it all together
def enrich_all_hosts(alive_hosts):
    enriched_alive_hosts = []
    with ThreadPoolExecutor(max_workers=50) as executor:
        results = executor.map(lambda host: enrich_single_host(host), alive_hosts)
        for result in results:
            enriched_alive_hosts.append(result)
    return enriched_alive_hosts

            
if __name__ == "__main__":
    subnet = "192.168.1.0/24"
    live = scan_subnet(subnet)
    output1 = enrich_all_hosts(live)
    print(f"discovered {len(live)} hosts.")
    print(f"{output1}")