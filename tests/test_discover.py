from unittest.mock import patch
from scanner import discover


def mock_socket_factory(connect_return=0):
    class DummySocket:
        def __init__(self, return_value):
            self.return_value = return_value
        def settimeout(self, timeout):
            pass
        def connect_ex(self, *args, **kwargs):
            return self.return_value
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            pass
    def factory(*args, **kwargs):
        return DummySocket(connect_return)
    return factory


def test_is_alive_open_port():
    with patch('scanner.discover.socket.socket', side_effect=mock_socket_factory(0)):
        ip = '192.168.1.1'
        assert discover.is_alive(ip) == ip


def test_is_alive_all_ports_closed():
    with patch('scanner.discover.socket.socket', side_effect=mock_socket_factory(1)):
        ip = '192.168.1.2'
        assert discover.is_alive(ip) is None


def test_enrich_single_host_keys():
    ip = '192.168.1.3'
    with patch('scanner.discover.get_hostname', return_value='host'):
        with patch('scanner.discover.get_mac', return_value='00:11:22:33:44:55'):
            with patch('scanner.discover.get_open_ports', return_value=[80]):
                result = discover.enrich_single_host(ip)
    assert isinstance(result, dict)
    assert set(result.keys()) == {'ip', 'hostname', 'mac', 'open_ports'}
