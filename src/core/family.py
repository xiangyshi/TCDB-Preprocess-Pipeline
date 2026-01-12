"""
Family entity representing a TCDB family.

This module contains the Family class that represents a TCDB family and manages
its protein systems, domain analysis, and visualization.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import pandas as pd
from .system import System
from .domain import Domain
from ..utils.file_utils import merge_overlapping_domains

import logging
logger = logging.getLogger(__name__)

@dataclass
class Family:
    """
    A TCDB family containing multiple protein systems.
    
    Attributes:
        family_id: TCDB family identifier
        systems: List of protein systems in this family
        output_directory: Directory for output files
        merge_overlapping: Whether to merge overlapping domains
        characteristic_domains: List of characteristic domain IDs
        statistics: Family statistics
    """
    
    family_id: str
    systems: List[System]
    output_directory: Path
    merge_overlapping: bool = True
    characteristic_domains: List[str] = field(default_factory=list)
    statistics: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize family after creation."""
        self._process_systems()
        self._calculate_statistics()
        self._identify_characteristic_domains()
        logger.info(f"Family {self.family_id} initialized with {len(self.systems)} systems")
        logger.info(f"Systems: {self.systems}")
        logger.info(f"Statistics: {self.statistics}")
        logger.info(f"Characteristic domains: {self.characteristic_domains}")
    
    def _process_systems(self):
        """Process all systems in the family."""
        for system in self.systems:
            if self.merge_overlapping:
                self._merge_system_domains(system)
            self._identify_system_holes(system)
    
    def _merge_system_domains(self, system: System):
        """Merge overlapping domains in a system."""
        # Get non-hole domains
        domains = [d for d in system.domains if not d.is_hole]
        
        if not domains:
            return
        
        # Convert to tuple format for compatibility (include evalue and rescue_round)
        domain_tuples = [(d.start, d.end, d.dom_id, d.bitscore, d.evalue, d.rescue_round) for d in domains]
        
        # Merge overlapping domains
        merged_tuples = merge_overlapping_domains(domain_tuples)
        
        # Convert back to Domain objects
        merged_domains = []
        for merged_tuple in merged_tuples:
            if len(merged_tuple) == 6:
                start, end, dom_id, bitscore, evalue, rescue_round = merged_tuple
            elif len(merged_tuple) == 5:
                start, end, dom_id, bitscore, rescue_round = merged_tuple
                evalue = 0.0
            else:
                # Handle old format without rescue_round
                start, end, dom_id, bitscore = merged_tuple
                evalue = 0.0
                rescue_round = None
            coverage = (end - start + 1) / system.sys_len
            domain = Domain(
                dom_id=dom_id,
                start=start,
                end=end,
                bitscore=bitscore,
                coverage=coverage,
                evalue=evalue,
                rescue_round=rescue_round
            )
            merged_domains.append(domain)
        
        # Update system domains
        system.domains = merged_domains
    
    def _identify_system_holes(self, system: System):
        """Identify inter-domain regions in a system."""
        # This is already handled in the System class
        pass
    
    def _calculate_statistics(self):
        """Calculate family statistics."""
        if not self.systems:
            self.statistics = {
                'num_systems': 0,
                'avg_protein_length': 0,
                'total_domains': 0,
                'unique_domains': set(),
                'domain_frequencies': {}
            }
            return
        
        # Calculate basic statistics
        total_length = sum(system.sys_len for system in self.systems)
        total_domains = sum(len([d for d in s.domains if not d.is_hole]) for s in self.systems)
        
        # Count domain frequencies
        domain_frequencies = {}
        unique_domains = set()
        
        for system in self.systems:
            for domain in system.domains:
                if not domain.is_hole:
                    unique_domains.add(domain.dom_id)
                    domain_frequencies[domain.dom_id] = domain_frequencies.get(domain.dom_id, 0) + 1
        
        self.statistics = {
            'num_systems': len(self.systems),
            'avg_protein_length': total_length / len(self.systems),
            'total_domains': total_domains,
            'unique_domains': list(unique_domains),
            'domain_frequencies': domain_frequencies
        }
    
    def _identify_characteristic_domains(self, threshold: float = 0.5):
        """Identify characteristic domains for this family."""
        if not self.systems:
            self.characteristic_domains = []
            return
        
        num_systems = len(self.systems)
        characteristic_domains = []
        
        for domain_id, frequency in self.statistics['domain_frequencies'].items():
            if frequency / num_systems >= threshold:
                characteristic_domains.append(domain_id)
        
        self.characteristic_domains = characteristic_domains
    
    def get_system_by_id(self, system_id: str) -> Optional[System]:
        """
        Get a system by its ID.
        
        Args:
            system_id: System identifier
            
        Returns:
            System object or None if not found
        """
        for system in self.systems:
            if system.sys_id == system_id:
                return system
        return None
    
    def get_systems_with_domain(self, domain_id: str) -> List[System]:
        """
        Get all systems that contain a specific domain.
        
        Args:
            domain_id: Domain identifier
            
        Returns:
            List of systems containing the domain
        """
        systems = []
        for system in self.systems:
            for domain in system.domains:
                if domain.dom_id == domain_id:
                    systems.append(system)
                    break
        return systems
    
    def get_domain_statistics(self) -> Dict:
        """
        Get detailed domain statistics for the family.
        
        Returns:
            Dictionary containing domain statistics
        """
        if not self.systems:
            return {}
        
        # Calculate domain statistics
        domain_stats = {}
        
        for system in self.systems:
            for domain in system.domains:
                if not domain.is_hole:
                    if domain.dom_id not in domain_stats:
                        domain_stats[domain.dom_id] = {
                            'count': 0,
                            'total_length': 0,
                            'avg_bitscore': 0,
                            'systems': set()
                        }
                    
                    stats = domain_stats[domain.dom_id]
                    stats['count'] += 1
                    stats['total_length'] += domain.length
                    stats['avg_bitscore'] += domain.bitscore
                    stats['systems'].add(system.sys_id)
        
        # Calculate averages
        for domain_id, stats in domain_stats.items():
            stats['avg_length'] = stats['total_length'] / stats['count']
            stats['avg_bitscore'] = stats['avg_bitscore'] / stats['count']
            stats['systems'] = list(stats['systems'])
        
        return domain_stats
    
    def generate_csv_data(self) -> List[List[str]]:
        """
        Generate CSV data for the family.
        
        Returns:
            List of CSV rows
        """
        csv_rows = []
        
        for system in self.systems:
            csv_row = system.generate_csv_row()
            csv_rows.append(csv_row)
        
        return csv_rows
    
    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert family data to a pandas DataFrame.
        
        Returns:
            DataFrame containing family data
        """
        data = []
        
        for system in self.systems:
            for domain in system.domains:
                row = {
                    'family_id': self.family_id,
                    'system_id': system.sys_id,
                    'accession': system.accession,
                    'protein_length': system.sys_len,
                    'domain_id': domain.dom_id,
                    'domain_start': domain.start,
                    'domain_end': domain.end,
                    'domain_length': domain.length,
                    'bitscore': domain.bitscore,
                    'evalue': domain.evalue,
                    'coverage': domain.coverage,
                    'domain_type': domain.type
                }
                data.append(row)
        
        return pd.DataFrame(data)
    
    def __repr__(self) -> str:
        return f"Family(id='{self.family_id}', systems={len(self.systems)})"
    
    def __str__(self) -> str:
        return f"TCDB Family {self.family_id} with {len(self.systems)} systems" 