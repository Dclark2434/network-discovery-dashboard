# network-discovery-dashboard
 

## Running Tests

Make sure pytest is installed and run tests from the repository root:

```bash
pytest
```

The application stores scan history in a SQLite database located at
`data/devices.db` by default. You can override the location by setting the
`DB_PATH` environment variable.
