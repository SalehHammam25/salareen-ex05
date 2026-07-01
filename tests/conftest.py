import os

# Force matplotlib to use the non-interactive Agg backend for all tests.
# This must be set before any matplotlib import occurs, so it belongs here
# in conftest.py which pytest loads before collecting test modules.
os.environ.setdefault("MPLBACKEND", "Agg")
