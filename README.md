# Network Discovery Dashboard

Simple dashboard for discovering devices on a local subnet.

## Quick Start

Install the required packages and launch the Flask application:

```bash
pip install -r requirements.txt
python web/app.py
```

The default subnet scanned is `192.168.1.0/24`. Edit `web/app.py` if you need to
scan a different range. Once running, visit `http://localhost:5000` to view the
dashboard.

## Running Tests

Make sure `pytest` is installed and run the tests from the repository root:

```bash
pytest
```
