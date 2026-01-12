"""
Command Line Interface for TCDB Domain Visualization.

This package contains the CLI components for the TCDB Domain Visualization tool.
"""

from .main import main
from .argument_parser import parse_arguments

__all__ = ["main", "parse_arguments"] 