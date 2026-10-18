"""The dhamaan command: one entry point for the repository's checks, rendering, case templates and log scoring.

Layer: command (above tools, sim and docsgen). It may import every layer below it and nothing imports it.
No network access, no external service. Local install only: python -m pip install -e .
"""
__version__ = "1.8.0"
