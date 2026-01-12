"""
Configuration management for TCDB Domain Visualization.

This module provides centralized configuration management with support for
environment variables and configuration files.
"""

import os
from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class Config:
    """
    Configuration settings for the TCDB Domain Visualization tool.
    
    Attributes:
        output_directory: Base output directory for results
        sequences_directory: Directory containing protein sequence files
        merge_overlapping_domains: Whether to merge overlapping domain hits
        default_plot_types: Default plot types to generate
        hole_threshold: Minimum length for inter-domain regions
        hole_margin: Margin around domains for hole detection
        characteristic_threshold: Threshold for characteristic domain identification
    """
    
    # Directories
    output_directory: str = "output/"
    sequences_directory: str = "data/sequences/"
    cdd_files_directory: str = "data/cdd_files/"
    rescue_files_directory: str = "data/rescue_files/"
    
    # Processing options
    merge_overlapping_domains: bool = True
    hole_threshold: int = 50
    hole_margin: int = 10
    characteristic_threshold: float = 0.5
    
    # Plot options
    default_plot_types: List[str] = field(default_factory=lambda: ["general", "char", "arch", "holes", "summary"])
    
    # File patterns
    sequence_file_pattern: str = "tcdb-{family_id}.faa"
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Create configuration from environment variables."""
        return cls(
            output_directory=os.getenv('TCDB_OUTPUT_DIR', 'output/'),
            sequences_directory=os.getenv('TCDB_SEQUENCES_DIR', 'data/sequences/'),
            cdd_files_directory=os.getenv('TCDB_CDD_DIR', 'data/cdd_files/'),
            rescue_files_directory=os.getenv('TCDB_RESCUE_DIR', 'data/rescue_files/'),
            merge_overlapping_domains=os.getenv('TCDB_MERGE_DOMAINS', 'true').lower() == 'true',
            hole_threshold=int(os.getenv('TCDB_HOLE_THRESHOLD', '50')),
            hole_margin=int(os.getenv('TCDB_HOLE_MARGIN', '10')),
            characteristic_threshold=float(os.getenv('TCDB_CHAR_THRESHOLD', '0.5')),
            default_plot_types=os.getenv('TCDB_DEFAULT_PLOTS', 'general,char,arch,holes,summary').split(',')
        )
    
    def get_sequence_file_path(self, family_id: str) -> str:
        """Get the path to a sequence file for a given family."""
        filename = self.sequence_file_pattern.format(family_id=family_id)
        return os.path.join(self.sequences_directory, filename)
    
    def get_output_path(self, family_id: str, plot_type: str) -> str:
        """Get the output path for a specific family and plot type."""
        return os.path.join(self.output_directory, "plots", plot_type, family_id)
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist."""
        directories = [
            self.output_directory,
            self.sequences_directory,
            self.cdd_files_directory,
            self.rescue_files_directory,
            os.path.join(self.output_directory, "plots"),
            os.path.join(self.output_directory, "csv")
        ]
        
        # Add plot type directories
        for plot_type in ["general", "char", "arch", "holes", "summary"]:
            directories.append(os.path.join(self.output_directory, "plots", plot_type))
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)


# Global configuration instance
config = Config.from_env() 