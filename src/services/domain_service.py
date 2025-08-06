"""
Domain service for TCDB Domain Visualization.

This module contains the business logic for domain analysis and processing.
"""

from typing import List, Dict, Tuple
from ..core.domain import Domain
from ..utils.file_utils import merge_overlapping_domains, find_holes


class DomainService:
    """
    Service for domain analysis and processing operations.
    """
    
    def __init__(self):
        """Initialize the domain service."""
        pass
    
    def merge_overlapping_domains(self, domains: List[Domain]) -> List[Domain]:
        """
        Merge overlapping domains with the same ID.
        
        Args:
            domains: List of domains to merge
            
        Returns:
            List of merged domains
        """
        if not domains:
            return []
        
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
            # Calculate coverage based on domain length (simplified approach)
            domain_length = end - start + 1
            # Use a reasonable default protein length for coverage calculation
            default_protein_length = 1000
            coverage = domain_length / default_protein_length
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
        
        return merged_domains
    
    def find_inter_domain_regions(self, domains: List[Domain], protein_length: int) -> List[Domain]:
        """
        Find inter-domain regions (holes) in a protein sequence.
        
        Args:
            domains: List of domains in the protein
            protein_length: Length of the protein sequence
            
        Returns:
            List of hole domains
        """
        # Extract domain regions
        domain_regions = [(d.start, d.end) for d in domains if not d.is_hole]
        
        # Find holes
        hole_tuples = find_holes(protein_length, domain_regions)
        
        # Convert to Domain objects
        holes = []
        for start, end, _, _ in hole_tuples:
            coverage = (end - start + 1) / protein_length
            hole = Domain(
                dom_id="-1",
                start=start,
                end=end,
                bitscore=-1,
                coverage=coverage,
                type="hole"
            )
            holes.append(hole)
        
        return holes
    
    def analyze_domain_composition(self, domains: List[Domain]) -> Dict:
        """
        Analyze the composition of domains in a protein.
        
        Args:
            domains: List of domains to analyze
            
        Returns:
            Dictionary containing domain composition analysis
        """
        analysis = {
            'total_domains': len([d for d in domains if not d.is_hole]),
            'total_holes': len([d for d in domains if d.is_hole]),
            'domain_types': {},
            'coverage': 0.0,
            'domain_lengths': [],
            'hole_lengths': []
        }
        
        total_coverage = 0.0
        
        for domain in domains:
            if domain.is_hole:
                analysis['hole_lengths'].append(domain.length)
            else:
                analysis['domain_lengths'].append(domain.length)
                total_coverage += domain.coverage
                
                # Count domain types
                domain_type = domain.dom_id
                analysis['domain_types'][domain_type] = analysis['domain_types'].get(domain_type, 0) + 1
        
        analysis['coverage'] = total_coverage
        
        return analysis
    
    def get_domain_statistics(self, domains: List[Domain]) -> Dict:
        """
        Calculate statistics for a list of domains.
        
        Args:
            domains: List of domains to analyze
            
        Returns:
            Dictionary containing domain statistics
        """
        if not domains:
            return {
                'count': 0,
                'avg_length': 0,
                'min_length': 0,
                'max_length': 0,
                'total_coverage': 0
            }
        
        lengths = [d.length for d in domains if not d.is_hole]
        coverages = [d.coverage for d in domains if not d.is_hole]
        
        stats = {
            'count': len(lengths),
            'avg_length': sum(lengths) / len(lengths) if lengths else 0,
            'min_length': min(lengths) if lengths else 0,
            'max_length': max(lengths) if lengths else 0,
            'total_coverage': sum(coverages) if coverages else 0
        }
        
        return stats
    
    def filter_domains_by_score(self, domains: List[Domain], min_score: float) -> List[Domain]:
        """
        Filter domains by minimum score.
        
        Args:
            domains: List of domains to filter
            min_score: Minimum score threshold
            
        Returns:
            List of domains above the score threshold
        """
        return [d for d in domains if d.bitscore >= min_score]
    
    def sort_domains_by_position(self, domains: List[Domain]) -> List[Domain]:
        """
        Sort domains by their start position in the protein.
        
        Args:
            domains: List of domains to sort
            
        Returns:
            Sorted list of domains
        """
        return sorted(domains, key=lambda x: x.start)
    
    def get_domain_overlaps(self, domains: List[Domain]) -> List[Tuple[Domain, Domain]]:
        """
        Find overlapping domains.
        
        Args:
            domains: List of domains to check for overlaps
            
        Returns:
            List of overlapping domain pairs
        """
        overlaps = []
        sorted_domains = self.sort_domains_by_position(domains)
        
        for i in range(len(sorted_domains)):
            for j in range(i + 1, len(sorted_domains)):
                if sorted_domains[i].overlaps_with(sorted_domains[j]):
                    overlaps.append((sorted_domains[i], sorted_domains[j]))
        
        return overlaps 