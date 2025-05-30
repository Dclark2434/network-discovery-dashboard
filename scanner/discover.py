import socket

def is_alive(ip):
    """A function that utilizes the socket module to check if port 80 is responding at
    the passed in IP.

    https://docs.python.org/3/library/socket.html#socket.socket.connect

    :param ip: string - The IPv4 address that we are checking."""
    try:
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((str(ip), 80))
        return str(ip)
    except:
        return None

def scan_subnet(subnet):
    pass

if __name__ == "__main__":
    subnet = "192.168.1.0/24"
    live = scan_subnet(subnet)
  #  print(f"discovered {len(live)} hosts.")