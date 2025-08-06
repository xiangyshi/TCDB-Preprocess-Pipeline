"""
Argument parser for TCDB Domain Visualization CLI.

This module provides argument parsing and validation for the command-line interface.
"""

import argparse
import logging
import os
from typing import Tuple, Optional
from ..utils.validation import (
    validate_file_path, 
    validate_directory_path, 
    validate_plot_types,
    validate_family_id_list,
    validate_merge_option,
    validate_output_directory
)

logger = logging.getLogger(__name__)

class ArgumentError(Exception):
    """Custom exception for argument validation errors."""
    pass


def parse_arguments() -> Tuple[argparse.Namespace, bool]:
    """
    Parse and validate command-line arguments.
    
    Returns:
        Tuple containing parsed arguments and flag indicating if TCID input is a file
        
    Raises:
        ArgumentError: If arguments are invalid
    """
    parser = argparse.ArgumentParser(
        description="Process protein domains using rpsblast and TCDB-specific proteins.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process CDD file with all plots
  python -m src.cli.main -c singles.cdd -p all -o results/
  
  # Process specific families
  python -m src.cli.main -c singles.cdd -t "1.A.12,2.A.1" -p "arch,summary"
  
  # Process rescue data
  python -m src.cli.main -r rescued/ -p char_rescue -o rescue_results/
        """
    )

    # Processing options
    parser.add_argument(
        "-m", "--merge-overlapping-domains",
        type=int,
        choices=[0, 1],
        default=1,
        help="Merge overlapping domain hits (1 = merge, 0 = do not merge). Default: 1"
    )

    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "-c", "--cdd-input",
        type=str,
        help="Path to input CDD file"
    )
    input_group.add_argument(
        "-r", "--rescue-input",
        type=str,
        help="Path to directory containing rescue files"
    )

    # Output options
    parser.add_argument(
        "-p", "--plot",
        type=str,
        default=None,
        help="Plot types to generate. CDD: all/general,char,arch,holes,summary. Rescue: all/char_rescue"
    )

    parser.add_argument(
        "-d", "--data",
        type=str,
        default="",
        help="Output CSV file for protein architecture data"
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        default="output/",
        help="Output directory. Default: output/"
    )

    parser.add_argument(
        "-t", "--tcids",
        type=str,
        default="",
        help="Target TCIDs to process. File path or comma-separated list (e.g., 1.A.12,2.A.1)"
    )

    # Logging options
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Default: INFO"
    )

    # Parse arguments
    args = parser.parse_args()
    
    # Validate arguments
    _validate_arguments(args)
    
    # Determine if TCID input is a file
    is_file = args.tcids and os.path.isfile(args.tcids)
    
    return args, is_file


def _validate_arguments(args: argparse.Namespace):
    """
    Validate parsed arguments.
    
    Args:
        args: Parsed arguments
        
    Raises:
        ArgumentError: If arguments are invalid
    """
    try:
        # Validate input files/directories
        if args.cdd_input:
            if not validate_file_path(args.cdd_input):
                raise ArgumentError(f"CDD input file not found: {args.cdd_input}")
        
        if args.rescue_input:
            if not validate_directory_path(args.rescue_input):
                raise ArgumentError(f"Rescue input directory not found: {args.rescue_input}")
        
        # Validate plot types
        if args.plot:
            validate_plot_types(args.plot)
        
        # Validate family IDs
        if args.tcids:
            validate_family_id_list(args.tcids)
        
        # Validate merge option
        validate_merge_option(args.merge_overlapping_domains)
        
        # Validate output directory
        validate_output_directory(args.output)
        
    except ValueError as e:
        raise ArgumentError(str(e))


def create_processing_config(args: argparse.Namespace) -> dict:
    """
    Create processing configuration from arguments.
    
    Args:
        args: Parsed arguments
        
    Returns:
        Configuration dictionary
    """
    logger.info(f"Creating processing configuration from arguments: {args}")
    return {
        'merge_overlapping_domains': bool(args.merge_overlapping_domains),
        'plot_types': args.plot.split(',') if args.plot else [],
        'output_directory': args.output,
        'data_file': args.data if args.data else None,
        'family_ids': args.tcids if args.tcids else None,
        'input_type': 'cdd' if args.cdd_input else 'rescue',
        'input_path': args.cdd_input or args.rescue_input
    } 