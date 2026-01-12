"""
CDD parser for TCDB Domain Visualization.

This module provides functionality for parsing CDD (Conserved Domain Database) files.
"""

import pandas as pd
from typing import Optional, List
import os
from io import StringIO

import logging
logger = logging.getLogger(__name__)

class CDDParser:
    """
    Parser for CDD (Conserved Domain Database) files.
    """
    
    pass
    
    def __init__(self):
        """Initialize the CDD parser."""
        pass
    
    def parse_file(self, file_path: str, family_ids: Optional[str] = None) -> pd.DataFrame:
        """
        Parse a CDD file and extract domain information.
        
        Args:
            file_path: Path to the CDD file
            family_ids: Optional list of family IDs to filter
            
        Returns:
            DataFrame containing parsed domain data
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CDD file not found: {file_path}")
        
        # Read and parse the CDD file
        data = self._read_cdd_file(file_path)
        
        # Filter by family IDs if provided
        if family_ids:
            data = self._filter_by_family_ids(data, family_ids)
        
        logger.info(f"Parsed data: {data.head()}")
        return data
    
    def _read_cdd_file(self, file_path: str) -> pd.DataFrame:
        """
        Read and parse a CDD file using the original cleaning logic.
        
        Args:
            file_path: Path to the CDD file
            
        Returns:
            DataFrame containing parsed data
        """
        try:
            # Obtain column headers
            header = None
            data_lines = []
            
            with open(file_path, 'r') as input_file:
                for line in input_file:
                    if line.startswith("# Fields:"):
                        header = line.strip().replace("# Fields: ", "")  # Extract and clean the header line
                    elif not line.startswith("#") and line.strip():  # Skip comments and empty lines
                        data_lines.append(line.strip())
            
            if not header:
                raise ValueError("Fields header not found in the input file.")
            
            if not data_lines:
                return pd.DataFrame()

            # Convert cleaned data to DataFrame
            cleaned_data = StringIO('\n'.join(data_lines))
            df = pd.read_csv(cleaned_data, sep='\t', header=None)

            # Set column names
            df.columns = header.split(", ")

            # Extract family ID from query accession
            df['family'] = df['query acc.'].apply(lambda x: '.'.join(x.split(".")[:3]))
            
            # Rename columns to match expected format
            df = df.rename(columns={
                'query acc.': 'accession',
                'family': 'family',
                'subject accs.': 'hit name',
                'q. start': 'hit start',
                'q. end': 'hit end'
            })
            
            # Add system column (using accession as system ID for now)
            df['system'] = df['accession']
            
            # Create domains column from hit coordinates
            df['domains'] = df.apply(self._create_domains_string, axis=1)
            
            return df
        
        except Exception as e:
            # Return empty df when error
            print("An error occurred during cleaning input/projection file:", e)
            return pd.DataFrame()
    
    def _create_domains_string(self, row) -> str:
        """
        Create a domains string from hit coordinates.
        
        Args:
            row: DataFrame row with hit coordinates
            
        Returns:
            String representation of domains
        """
        try:
            # Extract hit coordinates and create domain string
            # Format: domain_name:start-end
            hit_name = row.get('hit name', 'Unknown')
            hit_start = row.get('hit start', 0)
            hit_end = row.get('hit end', 0)
            
            return f"{hit_name}:{hit_start}-{hit_end}"
        except:
            return ""
    
    def _filter_by_family_ids(self, data: pd.DataFrame, family_ids: str) -> pd.DataFrame:
        """
        Filter data by family IDs.
        
        Args:
            data: DataFrame to filter
            family_ids: Family IDs to filter by
            
        Returns:
            Filtered DataFrame
        """
        if not family_ids or data.empty:
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
    
    def clean_cdd_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate CDD data.
        
        Args:
            data: Raw CDD data
            
        Returns:
            Cleaned DataFrame
        """
        if data.empty:
            return data
            
        # Remove rows with missing essential data
        cleaned_data = data.dropna(subset=['system', 'family'])
        
        # Remove rows with empty domains
        cleaned_data = cleaned_data[cleaned_data['domains'].str.strip() != '']
        
        return cleaned_data 