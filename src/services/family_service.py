"""
Family service for TCDB Domain Visualization.

This module contains the business logic for processing protein families
and managing family-related operations.
"""

import pandas as pd
from typing import List, Optional, Dict
from ..core.family import Family
from ..core.system import System
from ..core.domain import Domain, create_hole
from ..utils.file_utils import read_sequence_file
from ..utils.config import config
from ..parsers.cdd_parser import CDDParser
from ..parsers.rescue_parser import RescueParser

import logging
logger = logging.getLogger(__name__)

class FamilyService:
    """
    Service for processing protein families and managing family-related operations.
    """
    
    def __init__(self):
        """Initialize the family service."""
        self.cdd_parser = CDDParser()
        self.rescue_parser = RescueParser()
    
    def load_family_data(
        self, 
        input_path: str, 
        input_type: str, 
        family_ids: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Load family data from input files.
        
        Args:
            input_path: Path to input file or directory
            input_type: Type of input ('cdd' or 'rescue')
            family_ids: Optional list of family IDs to filter
            
        Returns:
            DataFrame containing family data
        """
        if input_type == 'cdd':
            return self.cdd_parser.parse_file(input_path, family_ids)
        elif input_type == 'rescue':
            return self.rescue_parser.parse_directory(input_path, family_ids)
        else:
            raise ValueError(f"Unsupported input type: {input_type}")
    
    def create_family(
        self, 
        family_data: pd.DataFrame, 
        family_id: str, 
        output_directory: str,
        merge_overlapping: bool = True,
        input_type: str = 'cdd'
    ) -> Family:
        """
        Create a Family object from family data.
        
        Args:
            family_data: DataFrame containing family data
            family_id: Family identifier
            output_directory: Output directory for results
            merge_overlapping: Whether to merge overlapping domains
            
        Returns:
            Family object
        """
        # Load sequences for this family
        sequence_file_path = config.get_sequence_file_path(family_id)
        sequence_map = read_sequence_file(sequence_file_path)
        
        # Create systems for this family using the original logic
        systems = self._get_systems(family_data, family_id, sequence_map, merge_overlapping)
        
        # Create family based on input type
        from pathlib import Path
        
        if input_type == 'rescue':
            from ..core.rescue_family import RescueFamily
            family = RescueFamily(
                rescue_data=family_data,
                family_id=family_id,
                output_directory=str(Path(output_directory)),
                merge_overlapping=merge_overlapping
            )
        else:
            family = Family(
                family_id=family_id,
                systems=systems,
                output_directory=Path(output_directory),
                merge_overlapping=merge_overlapping
            )
        
        return family
    
    def _get_systems(self, family_data: pd.DataFrame, family_id: str, sequence_map: dict, merge_overlapping: bool) -> List[System]:
        """
        Constructs System objects for each unique system in the family data.
        
        Args:
            family_data: DataFrame containing family data
            family_id: Family identifier
            sequence_map: Dictionary mapping system IDs to sequences
            merge_overlapping: Whether to merge overlapping domains
            
        Returns:
            List of constructed System objects
        """
        systems = []
        system_ids = family_data['system'].unique()
        
        for system_id in system_ids:
            # Get data for this system
            system_data = family_data[family_data['system'] == system_id]
            
            # Get sequence for this system
            sequence = sequence_map.get(system_id, "")
            sys_len = len(sequence)  # Ensure it's an integer
            
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"System {system_id}: sequence length={sys_len}")
            
            if sys_len <= 0:
                logger.warning(f"System {system_id}: sequence missing, skipping system")
                continue
            
            # Get domains for this system
            domains = self._get_domains(sys_len, system_data)
            # Merge overlapping domains if requested
            if merge_overlapping:
                domains = self._merge_domains(domains, sys_len)
            # Create system
            system = System(
                fam_id=family_id,
                sys_id=system_id,
                sys_len=sys_len,
                domains=domains,
                accession=system_id,
                sequence=sequence
            )
            systems.append(system)
        
        return systems
    
    def _get_domains(self, sys_len: int, system_data: pd.DataFrame) -> List[Domain]:
        """
        Retrieves domain information for a specific system.
        
        Args:
            sys_len: Total length of the system protein
            system_data: Data containing hits only within this system
            
        Returns:
            List of Domain objects (domains and holes)
        """
        domains = []
        
        # Try to get domain data with bitscore, fallback to evalue
        try:
            # Sort by start position
            sorted_data = system_data.sort_values('hit start')
            
            # Create domain objects from hit data
            for _, row in sorted_data.iterrows():
                try:
                    start = int(row['hit start'])
                    end = int(row['hit end'])
                    dom_id = row['hit name']
                    bitscore = float(row.get('bitscore', 0.0))
                    evalue = float(row.get('evalue', 0.0))
                    # Calculate coverage
                    if sys_len <= 0:
                        coverage = 0.0
                    else:
                        coverage = (end - start + 1) / sys_len
                        
                        # Clamp coverage to valid range
                        if coverage < 0 or coverage > 1:
                            coverage = max(0.0, min(1.0, coverage))
                    
                    # Get rescue round if available
                    rescue_round = row.get('rescue round', None)
                    if rescue_round is not None:
                        rescue_round = int(rescue_round)
                    
                    domain = Domain(
                        dom_id=dom_id,
                        start=start,
                        end=end,
                        bitscore=bitscore,
                        coverage=coverage,
                        evalue=evalue,
                        rescue_round=rescue_round
                    )
                    domains.append(domain)
                except (ValueError, KeyError) as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Error creating domain from row: {e}")
                    continue
                    
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error processing domain data: {e}")
        
        # Find holes (inter-domain regions)
        holes = self._find_holes(sys_len, domains)
        domains.extend(holes)
        
        # Sort all domains by start position
        domains.sort(key=lambda x: x.start)
        
        return domains
    
    def _find_holes(self, sys_len: int, domains: List[Domain]) -> List[Domain]:
        """
        Find inter-domain regions (holes) in a protein.
        
        Args:
            sys_len: Total protein length
            domains: List of domain objects
            
        Returns:
            List of hole Domain objects
        """
        try:
            holes = []
            
            if not domains:
                return holes
            
            # Sort domains by start position
            sorted_domains = sorted(domains, key=lambda x: x.start)
            
            # Find gaps between domains
            current_pos = 1
            
            for domain in sorted_domains:
                if domain.start > current_pos:
                    # Create hole from current_pos to domain.start - 1
                    hole = create_hole(
                        start=current_pos,
                        end=domain.start - 1,
                        protein_length=sys_len
                    )
                    holes.append(hole)
                
                current_pos = max(current_pos, domain.end + 1)
            
            # Check for hole at the end
            if current_pos <= sys_len:
                hole = create_hole(
                    start=current_pos,
                    end=sys_len,
                    protein_length=sys_len
                )
                holes.append(hole)
            
            return holes
        except Exception as e:
            logger.error(f"Error finding holes: {e}")
            return []
    
    def _merge_domains(self, domains: List[Domain], sys_len: int = None) -> List[Domain]:
        """
        Merge overlapping domains.
        
        Args:
            domains: List of domain objects
            sys_len: System length for coverage calculation
            
        Returns:
            List of merged domain objects
        """
        if not domains:
            return domains
        
        # Filter out holes for merging
        non_hole_domains = [d for d in domains if not d.is_hole]
        holes = [d for d in domains if d.is_hole]
        
        if not non_hole_domains:
            return holes
        
        # Convert to tuples for merging (include evalue and rescue_round)
        domain_tuples = [(d.start, d.end, d.dom_id, d.bitscore, d.evalue, d.rescue_round) for d in non_hole_domains]
        
        # Use the existing merge function
        from ..utils.file_utils import merge_overlapping_domains
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
            
            # Calculate coverage using actual system length if available
            if sys_len and sys_len > 0:
                coverage = (end - start + 1) / sys_len
            else:
                coverage = (end - start + 1) / 1000  # Fallback to average protein length
            
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
        
        # Add holes back and sort
        all_domains = merged_domains + holes
        all_domains.sort(key=lambda x: x.start)
        
        return all_domains
    

    
    def generate_csv_data(self, family: Family) -> List[List[str]]:
        """
        Generate CSV data for a family.
        
        Args:
            family: Family object
            
        Returns:
            List of CSV rows
        """
        csv_rows = []
        
        for system in family.systems:
            csv_row = system.generate_csv_row()
            csv_rows.append(csv_row)
        
        return csv_rows
    
    def get_characteristic_domains(self, family: Family, threshold: float = 0.5) -> List[str]:
        """
        Get characteristic domains for a family.
        
        Args:
            family: Family object
            threshold: Threshold for characteristic domain identification
            
        Returns:
            List of characteristic domain IDs
        """
        # Count domain occurrences across all systems
        domain_counts = {}
        total_systems = len(family.systems)
        
        for system in family.systems:
            for domain in system.domains:
                if not domain.is_hole:
                    domain_counts[domain.dom_id] = domain_counts.get(domain.dom_id, 0) + 1
        
        # Find domains that appear in more than threshold fraction of systems
        characteristic_domains = []
        for domain_id, count in domain_counts.items():
            if count / total_systems > threshold:  # Changed from >= to > to match original logic
                characteristic_domains.append(domain_id)
        
        return characteristic_domains
    
    def analyze_family_statistics(self, family: Family) -> Dict:
        """
        Analyze statistics for a family.
        
        Args:
            family: Family object
            
        Returns:
            Dictionary containing family statistics
        """
        stats = {
            'family_id': family.family_id,
            'num_systems': len(family.systems),
            'avg_protein_length': 0,
            'total_domains': 0,
            'unique_domains': set(),
            'domain_frequencies': {}
        }
        
        if family.systems:
            # Calculate average protein length
            total_length = sum(system.sys_len for system in family.systems)
            stats['avg_protein_length'] = total_length / len(family.systems)
            
            # Analyze domains
            for system in family.systems:
                stats['total_domains'] += len([d for d in system.domains if not d.is_hole])
                
                for domain in system.domains:
                    if not domain.is_hole:
                        stats['unique_domains'].add(domain.dom_id)
                        stats['domain_frequencies'][domain.dom_id] = \
                            stats['domain_frequencies'].get(domain.dom_id, 0) + 1
            
            # Convert set to list for JSON serialization
            stats['unique_domains'] = list(stats['unique_domains'])
        
        return stats 