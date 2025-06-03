import ipaddress
import re

def sanitize_subnet(subnet: str) -> str:
    """Validate and normalize a subnet string.

    Parameters
    ----------
    subnet: str
        The user provided subnet.

    Returns
    -------
    str
        The canonicalized subnet.

    Raises
    ------
    ValueError
        If the subnet is not valid.
    """
    if not re.fullmatch(r'[0-9./]+', subnet.strip()):
        raise ValueError('Invalid subnet format')
    network = ipaddress.ip_network(subnet, strict=False)
    return str(network)
