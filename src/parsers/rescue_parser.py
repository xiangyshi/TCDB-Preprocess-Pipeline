"""
Rescue parser for TCDB Domain Visualization.

This module provides functionality for parsing rescue files.
"""

import pandas as pd
import os
import csv
from typing import Optional, List


class RescueParser:
    """
    Parser for rescue files.
    """
    
    def __init__(self):
        """Initialize the rescue parser."""
        pass
    
    def parse_directory(self, directory_path: str, family_ids: Optional[str] = None) -> pd.DataFrame:
        """
        Parse rescue files in a directory.
        
        Args:
            directory_path: Path to directory containing rescue files
            family_ids: Optional list of family IDs to filter
            
        Returns:
            DataFrame containing parsed rescue data
        """
        if not os.path.isdir(directory_path):
            raise FileNotFoundError(f"Rescue directory not found: {directory_path}")
        
        # Find all rescue files in the directory
        rescue_files = self._find_rescue_files(directory_path)
        
        # Parse each file and combine data
        all_data = []
        for file_path in rescue_files:
            try:
                file_data = self._parse_rescue_file(file_path)
                if not file_data.empty:
                    all_data.append(file_data)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Error processing rescue file {file_path}: {e}")
                continue
        
        # Combine all DataFrames
        if all_data:
            data = pd.concat(all_data, ignore_index=True)
        else:
            data = pd.DataFrame()
        
        # Filter by family IDs if provided
        if family_ids and not data.empty:
            data = self._filter_by_family_ids(data, family_ids)
        
        return data
    
    def _find_rescue_files(self, directory_path: str) -> List[str]:
        """
        Find all rescue files in a directory.
        
        Args:
            directory_path: Directory to search
            
        Returns:
            List of rescue file paths
        """
        rescue_files = []
        
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            if os.path.isfile(file_path) and self._is_rescue_file(filename):
                rescue_files.append(file_path)
        
        return rescue_files
    
    def _is_rescue_file(self, filename: str) -> bool:
        """
        Check if a file is a rescue file.
        
        Args:
            filename: Name of the file
            
        Returns:
            True if the file is a rescue file
        """
        # Look for files ending with _rescuedDomains.tsv
        return filename.endswith("_rescuedDomains.tsv")
    
    def _parse_rescue_file(self, file_path: str) -> pd.DataFrame:
        """
        Parse a single rescue file.
        
        Args:
            file_path: Path to the rescue file
            
        Returns:
            DataFrame containing parsed data
        """
        # Initialize data structures to store parsed information
        rows = []  # Will store individual domain hits
        summary = []  # Will store domain summary statistics
        significant_domain_hits = {}  # Tracks count of significant hits per domain
        
        with open(file_path, "r") as file:
            reader = csv.reader(file, delimiter='\t')
            for line in reader:
                # Process header lines that start with '#'
                if line[0][0] == "#":
                    # Example line: '# CDD166458:  DirectHits:  9    Rescued Proteins:  2    Prots with Domain in 1.A.12:  11 (100.0% from a total of 11)'
                    dom = line[0].split(":")[0][2:]  # Extract domain ID (removing '# ' prefix)
                    found = 0  # Initialize found count
                    total = int(line[0].split("of")[1][:-1].strip())  # Extract total protein count
                    summary.append([dom, found, total])
                    continue
                
                # Process data lines
                sys_id, sys_len = line[1].split(":")  # Extract system ID and length
                sys_len = int(sys_len)
                
                # Process each domain hit in the line
                for domain in line[2:]:
                    parts = domain.split("|")  # Split domain information
                    dom_id = parts[0]  # Domain ID
                    
                    # Skip if no hit was found
                    if len(parts) < 3:
                        continue
                    
                    round_type = parts[-1]

                    for i in range(1, len(parts) - 1):
                        # Extract start and end positions
                        pos = parts[i].split(":")[0]  # Position information
                        start, end = pos.split("-")
                        start = int(start)
                        end = int(end)

                        # Track significant hits (DirectHit or Rescued1)
                        if round_type in ["DirectHit", "Rescued1"]:
                            if dom_id in significant_domain_hits:
                                significant_domain_hits[dom_id] += 1
                            else:
                                significant_domain_hits[dom_id] = 1

                        # Extract e-value and determine rescue round
                        evalue = float(parts[1].split(":")[1])
                        rounds = 1 if "1" in parts[2] else 2 if "2" in parts[2] else 0
                        rows.append([sys_id, sys_len, dom_id, start, end, evalue, rounds])
        
        # Update summary with actual found counts
        for row in summary:
            try:
                row[1] = significant_domain_hits[row[0]]
            except KeyError:
                continue

        # Create DataFrame from parsed domain hits
        df_rows = pd.DataFrame(rows, columns=["system", "query length", "hit name", "hit start", "hit end", "evalue", "rescue round"])
        
        # Create and process summary DataFrame
        df_summary = pd.DataFrame(summary, columns=["domain", "found", "total"])
        df_summary["perc found"] = df_summary["found"] / df_summary["total"]  # Calculate percentage of found domains
        # Filter domains with at least 80% found rate and sort by percentage
        df_summary = df_summary[df_summary["perc found"] >= 0.8].sort_values("perc found", ascending=False)

        # Get list of filtered domains
        filtered_domains = list(df_summary["domain"])
        # Filter rows to only include domains that meet the threshold
        df_rows = df_rows[df_rows["hit name"].isin(filtered_domains)]
        # Add family information by extracting first three parts of the query accession
        df_rows["family"] = df_rows["system"].apply(lambda x: '.'.join(x.split(".")[:3]))
        
        return df_rows
    
    def _filter_by_family_ids(self, data: pd.DataFrame, family_ids: str) -> pd.DataFrame:
        """
        Filter data by family IDs.
        
        Args:
            data: DataFrame to filter
            family_ids: Family IDs to filter by
            
        Returns:
            Filtered DataFrame
        """
        if not family_ids:
            return data
        
        # Parse family IDs
        if os.path.isfile(family_ids):
            # Read from file
            with open(family_ids, 'r') as f:
                target_families = [line.strip() for line in f if line.strip()]
        else:
            # Parse comma-separated list
            target_families = [fid.strip() for fid in family_ids.split(',') if fid.strip()]
        
        # Filter data
        filtered_data = data[data['family'].isin(target_families)]
        
        return filtered_data
    
    def clean_rescue_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate rescue data.
        
        Args:
            data: Raw rescue data
            
        Returns:
            Cleaned DataFrame
        """
        # Remove rows with missing essential data
        cleaned_data = data.dropna(subset=['system', 'family'])
        
        # Validate family IDs
        # Implementation would depend on validation requirements
        
        return cleaned_data 