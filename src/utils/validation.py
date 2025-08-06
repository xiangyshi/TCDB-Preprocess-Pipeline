"""
Validation utilities for TCDB Domain Visualization.

This module provides validation functions for input data, file paths,
and configuration parameters.
"""

import os
import re
from typing import List, Optional, Union


def validate_tcid_format(tcid: str) -> bool:
    """
    Validate TCDB family ID format.
    
    Args:
        tcid: TCDB family ID to validate
        
    Returns:
        True if format is valid
    """
    # TCDB format: X.X.X or X.X.X.X (e.g., 1.A.12, 2.A.1.1)
    pattern = r'^\d+\.\w+\.\d+(\.\d+)?$'
    return bool(re.match(pattern, tcid))


def validate_file_path(file_path: str, must_exist: bool = True) -> bool:
    """
    Validate a file path.
    
    Args:
        file_path: Path to validate
        must_exist: Whether the file must exist
        
    Returns:
        True if path is valid
    """
    if not file_path or not isinstance(file_path, str):
        return False
    
    if must_exist and not os.path.isfile(file_path):
        return False
    
    return True


def validate_directory_path(dir_path: str, must_exist: bool = True) -> bool:
    """
    Validate a directory path.
    
    Args:
        dir_path: Directory path to validate
        must_exist: Whether the directory must exist
        
    Returns:
        True if path is valid
    """
    if not dir_path or not isinstance(dir_path, str):
        return False
    
    if must_exist and not os.path.isdir(dir_path):
        return False
    
    return True


def validate_plot_types(plot_types: Union[str, List[str]]) -> List[str]:
    """
    Validate and normalize plot types.
    
    Args:
        plot_types: Plot types to validate (string or list)
        
    Returns:
        List of valid plot types
        
    Raises:
        ValueError: If invalid plot types are provided
    """
    valid_types = {
        "general", "char", "arch", "holes", "summary", 
        "char_rescue", "all"
    }
    
    if isinstance(plot_types, str):
        if plot_types == "all":
            return ["general", "char", "arch", "holes", "summary"]
        # Handle comma-separated plot types
        plot_types = [pt.strip() for pt in plot_types.split(',') if pt.strip()]
    
    if not isinstance(plot_types, list):
        raise ValueError("Plot types must be a string or list")
    
    # Validate each plot type
    invalid_types = set(plot_types) - valid_types
    if invalid_types:
        raise ValueError(f"Invalid plot types: {invalid_types}")
    
    return plot_types


def validate_domain_data(domains: List[tuple]) -> bool:
    """
    Validate domain data format.
    
    Args:
        domains: List of domain tuples (start, end, id, bitscore)
        
    Returns:
        True if data format is valid
    """
    if not isinstance(domains, list):
        return False
    
    for domain in domains:
        if not isinstance(domain, tuple) or len(domain) != 4:
            return False
        
        start, end, dom_id, bitscore = domain
        
        # Validate types
        if not isinstance(start, int) or not isinstance(end, int):
            return False
        if not isinstance(dom_id, str):
            return False
        if not isinstance(bitscore, (int, float)):
            return False
        
        # Validate values
        if start < 1 or end < start:
            return False
        if not dom_id:
            return False
    
    return True


def validate_sequence_data(sequence: str) -> bool:
    """
    Validate protein sequence data.
    
    Args:
        sequence: Protein sequence string
        
    Returns:
        True if sequence is valid
    """
    if not isinstance(sequence, str):
        return False
    
    if not sequence:
        return False
    
    # Check for valid amino acid characters
    valid_chars = set("ACDEFGHIKLMNPQRSTVWY")
    sequence_chars = set(sequence.upper())
    
    return sequence_chars.issubset(valid_chars)


def validate_family_id_list(family_ids: Union[str, List[str]]) -> List[str]:
    """
    Validate a list of family IDs.
    
    Args:
        family_ids: Family IDs to validate (string or list)
        
    Returns:
        List of valid family IDs
        
    Raises:
        ValueError: If invalid family IDs are provided
    """
    if isinstance(family_ids, str):
        # Check if it's a file path
        if os.path.isfile(family_ids):
            with open(family_ids, 'r') as f:
                family_ids = [line.strip() for line in f if line.strip()]
        else:
            # Parse comma-separated list
            family_ids = [fid.strip() for fid in family_ids.split(',') if fid.strip()]
    
    if not isinstance(family_ids, list):
        raise ValueError("Family IDs must be a string or list")
    
    # Validate each family ID
    invalid_ids = []
    valid_ids = []
    
    for fid in family_ids:
        if validate_tcid_format(fid):
            valid_ids.append(fid)
        else:
            invalid_ids.append(fid)
    
    if invalid_ids:
        raise ValueError(f"Invalid family IDs: {invalid_ids}")
    
    return valid_ids


def validate_merge_option(merge: Union[int, bool]) -> bool:
    """
    Validate merge overlapping domains option.
    
    Args:
        merge: Merge option to validate
        
    Returns:
        Boolean value for merge option
    """
    if isinstance(merge, bool):
        return merge
    elif isinstance(merge, int):
        return bool(merge)
    else:
        raise ValueError("Merge option must be boolean or integer (0/1)")


def validate_output_directory(output_dir: str) -> str:
    """
    Validate and normalize output directory path.
    
    Args:
        output_dir: Output directory path
        
    Returns:
        Normalized output directory path
        
    Raises:
        ValueError: If output directory is invalid
    """
    if not output_dir:
        raise ValueError("Output directory cannot be empty")
    
    # Normalize path
    output_dir = os.path.normpath(output_dir)
    
    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    return output_dir 