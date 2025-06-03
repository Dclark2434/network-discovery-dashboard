# Network Discovery Dashboard

Simple dashboard for discovering devices on a local subnet. The discovery
process performs a lightweight ping sweep of every host in the specified
subnet and then gathers additional details for any responding device.

## Quick Start

Install the required packages and ensure the `nmap` command is available (root privileges improve OS detection), then launch the Flask application:

```bash
pip install -r requirements.txt
python web/app.py
```

Once running, visit `http://localhost:5000` and enter the subnet you want to
scan. The scanner only runs when you submit the form, defaulting to
`192.168.1.0/24` if no subnet is provided.

Nmap is used for OS fingerprinting and for detecting open ports. If `nmap`
is not installed, the application falls back to a basic socket-based port
scan but OS information may be unavailable.

## Running Tests

Make sure `pytest` is installed and run the tests from the repository root:

```bash
pytest
```

The application stores scan history in a SQLite database located at
`data/devices.db` by default. You can override the location by setting the
`DB_PATH` environment variable.
