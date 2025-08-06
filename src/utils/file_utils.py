"""
File utility functions for TCDB Domain Visualization.

This module provides utility functions for file operations, including
reading sequences, parsing files, and managing file paths.
"""

import os
import csv
from typing import Dict, List, Optional, Tuple
from pathlib import Path


def read_sequence_file(file_path: str) -> Dict[str, str]:
    """
    Read protein sequences from a FASTA file.
    
    Args:
        file_path: Path to the FASTA file
        
    Returns:
        Dictionary mapping sequence IDs to sequences
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file format is invalid
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Sequence file not found: {file_path}")
    
    sequence_map = {}
    
    try:
        with open(file_path, 'r') as file:
            current_id = None
            current_sequence = []
            
            for line in file:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('>'):
                    # Save previous sequence if exists
                    if current_id and current_sequence:
                        sequence_map[current_id] = ''.join(current_sequence)
                    
                    # Start new sequence
                    current_id = line[1:]  # Remove '>' prefix
                    current_sequence = []
                else:
                    # Add to current sequence
                    current_sequence.append(line)
            
            # Save last sequence
            if current_id and current_sequence:
                sequence_map[current_id] = ''.join(current_sequence)
                
    except Exception as e:
        raise ValueError(f"Error reading sequence file {file_path}: {e}")
    
    return sequence_map


def write_csv_data(data: List[List[str]], file_path: str, headers: Optional[List[str]] = None):
    """
    Write data to a CSV file.
    
    Args:
        data: List of rows to write
        file_path: Path to the output CSV file
        headers: Optional list of column headers
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        
        if headers:
            writer.writerow(headers)
        
        writer.writerows(data)


def ensure_directory(path: str) -> str:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path to ensure
        
    Returns:
        The normalized path
    """
    os.makedirs(path, exist_ok=True)
    return os.path.normpath(path)


def get_file_extension(file_path: str) -> str:
    """
    Get the file extension from a file path.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File extension (including the dot)
    """
    return Path(file_path).suffix


def is_valid_file(file_path: str, required_extensions: Optional[List[str]] = None) -> bool:
    """
    Check if a file exists and has a valid extension.
    
    Args:
        file_path: Path to the file
        required_extensions: List of valid file extensions (e.g., ['.txt', '.csv'])
        
    Returns:
        True if file exists and has valid extension
    """
    if not os.path.isfile(file_path):
        return False
    
    if required_extensions:
        file_ext = get_file_extension(file_path)
        return file_ext.lower() in [ext.lower() for ext in required_extensions]
    
    return True


def find_files_by_pattern(directory: str, pattern: str) -> List[str]:
    """
    Find files in a directory matching a pattern.
    
    Args:
        directory: Directory to search in
        pattern: File pattern to match (e.g., "*.faa")
        
    Returns:
        List of matching file paths
    """
    if not os.path.isdir(directory):
        return []
    
    matching_files = []
    for file in os.listdir(directory):
        if file.endswith(pattern.replace('*', '')):
            matching_files.append(os.path.join(directory, file))
    
    return matching_files


def merge_overlapping_domains(domains: List[Tuple[int, int, str, float, float, Optional[int]]]) -> List[Tuple[int, int, str, float, float, Optional[int]]]:
    """
    Merge overlapping domains with the same ID.
    
    Args:
        domains: List of domain tuples (start, end, id, bitscore, evalue, rescue_round)
        
    Returns:
        List of merged domains
    """
    if not domains:
        return []
    
    # Sort by start position
    sorted_domains = sorted(domains, key=lambda x: x[0])
    merged = []
    current = list(sorted_domains[0])
    
    for domain_tuple in sorted_domains[1:]:
        if len(domain_tuple) == 6:
            start, end, dom_id, bitscore, evalue, rescue_round = domain_tuple
        else:
            # Handle old format without evalue and rescue_round
            start, end, dom_id, bitscore = domain_tuple
            evalue = 0.0
            rescue_round = None
            
        # Check if domains overlap and have same ID
        if (dom_id == current[2] and 
            start <= current[1] + 1):  # +1 to allow adjacent domains
            # Merge domains
            current[1] = max(current[1], end)
            current[3] = max(current[3], bitscore)
            # Keep the most significant e-value (smallest value)
            if len(current) >= 5:
                current_evalue = current[4]
                # Handle None values - treat None as 0.0 (least significant)
                if evalue is None:
                    evalue = 0.0
                if current_evalue is None:
                    current_evalue = 0.0
                if evalue < current_evalue or current_evalue == 0.0:
                    current[4] = evalue
            else:
                current.append(evalue)
                current.append(rescue_round)
        else:
            # No overlap, add current to merged list
            merged.append(tuple(current))
            current = [start, end, dom_id, bitscore, evalue, rescue_round]
    
    # Add the last domain
    merged.append(tuple(current))
    
    return merged


def find_holes(protein_length: int, domain_regions: List[Tuple[int, int]]) -> List[Tuple[int, int, str, str]]:
    """
    Find inter-domain regions (holes) in a protein sequence.
    
    Args:
        protein_length: Length of the protein sequence
        domain_regions: List of domain regions as (start, end) tuples
        
    Returns:
        List of holes as (start, end, "-1", "-1") tuples
    """
    # Create binary mask of covered positions
    covered = [False] * protein_length
    
    # Mark covered positions
    for start, end in domain_regions:
        for i in range(start - 1, min(end, protein_length)):
            covered[i] = True
    
    # Find continuous uncovered regions
    holes = []
    hole_start = None
    
    for i in range(protein_length):
        if not covered[i]:
            if hole_start is None:
                hole_start = i + 1  # Convert to 1-based index
        else:
            if hole_start is not None:
                holes.append((hole_start, i, "-1", "-1"))
                hole_start = None
    
    # Handle hole at the end
    if hole_start is not None:
        holes.append((hole_start, protein_length, "-1", "-1"))
    
    return holes


def confidence_interval_mean(coords: List[float], confidence_level: float = 0.95) -> float:
    """
    Calculates the confidence interval mean for a set of coordinates.
    
    Args:
        coords: List of coordinate values
        confidence_level: Confidence level (0 to 1), defaults to 0.95
        
    Returns:
        Mean value of the confidence interval
    """
    import numpy as np
    from scipy import stats
    
    if len(set(coords)) == 1:
        return np.mean(coords)
    
    mean = np.mean(coords)
    std_err = stats.sem(coords)
    df = len(coords) - 1
    
    ci = stats.t.interval(confidence_level, df, loc=mean, scale=std_err)
    return np.mean(ci)


def find_margins(domains: List, margin_left: int, margin_right: int) -> tuple:
    """
    Identifies domains that overlap with specified margin regions.
    
    Args:
        domains: List of Domain objects
        margin_left: Left margin position
        margin_right: Right margin position
        
    Returns:
        tuple: (left_domains, right_domains) Lists of domains overlapping
               with left and right margins respectively
    """
    left_doms = []
    right_doms = []
    
    for dom in domains:
        if dom.start <= margin_left and margin_left <= dom.end:
            left_doms.append(dom)
        if dom.start <= margin_right and margin_right <= dom.end:
            right_doms.append(dom)
    
    return left_doms, right_doms


def compare_reference(hole1, hole2) -> bool:
    """
    Compares two holes to determine if they share reference domains.
    
    Args:
        hole1: First hole object
        hole2: Second hole object
        
    Returns:
        bool: True if holes share at least one reference domain pair
    """
    return len(hole1.names & hole2.names) != 0


def get_connected_components(n: int, pair_list: List[List[int]]) -> List[set]:
    """
    Groups synonymous holes using a graph-based approach.
    
    Args:
        n: Total number of holes
        pair_list: List of hole pairs that are synonymous
        
    Returns:
        list: List of sets, each containing indices of synonymous holes
    """
    import networkx as nx
    
    G = nx.Graph()
    
    # Add all nodes (0-indexed)
    G.add_nodes_from(range(0, n))
    
    # Add all edges (the pairs from the pair_list)
    G.add_edges_from(pair_list)
    
    # Get connected components
    connected_components = list(nx.connected_components(G))
    
    return connected_components


def combine_svgs(svgs: List[str], filename: str, output_dir: str, plot_type: str = None) -> None:
    """
    Combines multiple SVG files into a single HTML file.
    
    Args:
        svgs: List of paths to SVG files
        filename: Output HTML filename
        output_dir: Output directory path
        plot_type: Type of plot (e.g., 'general', 'char', 'arch', 'holes', 'summary')
    """
    html_content = '<!DOCTYPE html>\n<html>\n<head>\n<title>Domain Visualization</title>\n</head>\n<body>\n'
    
    for svg in svgs:
        try:
            with open(svg, 'r') as file:
                svg_content = file.read().strip()
                # Ensure the SVG content is well-formed and includes the correct XML namespaces
                html_content += f'<div>{svg_content}</div>\n'
            os.remove(svg)  # Remove the original SVG file
        except FileNotFoundError:
            continue
    
    html_content += '</body>\n</html>'
    
    # Create organized directory structure if plot_type is provided
    if plot_type:
        plot_dir = os.path.join(output_dir, "plots", plot_type)
        os.makedirs(plot_dir, exist_ok=True)
        output_path = os.path.join(plot_dir, filename)
    else:
        output_path = os.path.join(output_dir, filename)
    
    with open(output_path, "w") as f:
        f.write(html_content)


def score_domain(domain, protein_length: float) -> float:
    """
    Calculate a score for a domain based on its coverage and e-value.
    
    Args:
        domain: Domain object with start, end, and evalue attributes
        protein_length: Total length of the protein
        
    Returns:
        Domain score
    """
    import numpy as np
    
    # Handle None evalue
    if domain.evalue is None:
        nlog = 1000000  # Default high score for domains without e-value
    else:
        # suppress divide by zero warnings
        with np.errstate(divide='ignore'):
            nlog = -np.log(domain.evalue)
            
        # Handle inf values when evalue is 0
        if np.isinf(nlog) or np.isnan(nlog):
            nlog = 1000000
    
    return (domain.end - domain.start / protein_length) * nlog

def is_overlap(dom1, dom2, mutual_overlap: float = 0.2) -> bool:
    """
    Check if two domains overlap based on mutual overlap threshold.
    
    Args:
        dom1: First domain object with start and end attributes
        dom2: Second domain object with start and end attributes
        mutual_overlap: Minimum required overlap fraction (0 to 1)
        
    Returns:
        True if the domains overlap, False otherwise
    """
    # Calculate the overlap
    overlap_start = max(dom1.start, dom2.start)
    overlap_end = min(dom1.end, dom2.end)

    # If there is no overlap
    if overlap_start >= overlap_end:
        return False

    # Calculate the lengths of the domains
    length_dom1 = dom1.end - dom1.start
    length_dom2 = dom2.end - dom2.start

    # Calculate the mutual overlap
    overlap_length = overlap_end - overlap_start
    shorter_length = min(length_dom1, length_dom2)
    
    # Check if the overlap meets the mutual overlap requirement
    return (overlap_length / shorter_length) >= mutual_overlap 