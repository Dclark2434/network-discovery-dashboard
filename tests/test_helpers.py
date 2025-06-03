import pytest
from utils.helpers import sanitize_subnet


def test_sanitize_subnet_valid():
    assert sanitize_subnet('192.168.1.0/24') == '192.168.1.0/24'


def test_sanitize_subnet_invalid():
    with pytest.raises(ValueError):
        sanitize_subnet("1.1.1.0/24; DROP TABLE")
