from unittest.mock import patch, MagicMock
from scanner import discover


def test_is_alive_ping_success():
    mock_result = MagicMock(returncode=0)
    with patch('scanner.discover.subprocess.run', return_value=mock_result):
        ip = '192.168.1.1'
        assert discover.is_alive(ip) == ip


def test_is_alive_ping_failure():
    mock_result = MagicMock(returncode=1)
    with patch('scanner.discover.subprocess.run', return_value=mock_result):
        ip = '192.168.1.2'
        assert discover.is_alive(ip) is None


def test_enrich_single_host_keys():
    ip = '192.168.1.3'
    with patch('scanner.discover.get_hostname', return_value='host'):
        with patch('scanner.discover.get_mac', return_value='00:11:22:33:44:55'):
            with patch('scanner.discover.get_os', return_value='Linux'):
                with patch('scanner.discover.get_open_ports', return_value=[80]):
                    result = discover.enrich_single_host(ip)
    assert isinstance(result, dict)
    assert set(result.keys()) == {'ip', 'hostname', 'mac', 'os', 'open_ports'}


def test_get_os_and_mac_parse():
    sample_output = """
Host is up (0.001s latency).
MAC Address: 00:11:22:33:44:55 (Vendor)
OS details: Linux 3.X
"""
    with patch('scanner.discover.subprocess.check_output', return_value=sample_output.encode()):
        os_name, mac = discover.get_os_and_mac('1.1.1.1')
    assert os_name == 'Linux 3.X'
    assert mac == '00:11:22:33:44:55'
