# src/vanta/__init__.py

from .metadata import __version__, __desc__

from .console import Console
from .table import Table

__all__ = [
    "Console",
    "Table"
]