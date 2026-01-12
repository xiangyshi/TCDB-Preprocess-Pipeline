"""
System entity representing a single protein system within a TCDB family.

This module contains the System class that represents a single protein system
and manages its domains and inter-domain regions.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from .domain import Domain
from .hole import Hole

import logging
logger = logging.getLogger(__name__)

@dataclass
class System:
    """
    A single protein system and its domain architecture.
    
    Attributes:
        fam_id: TCDB family identifier
        sys_id: Unique system identifier
        sys_len: Length of the protein sequence
        domains: List of Domain objects in order of appearance
        accession: Protein accession number
        sequence: Amino acid sequence
        holes: List of inter-domain regions
        domain_map: Mapping of domain IDs to Domain objects
    """
    
    fam_id: str
    sys_id: str
    sys_len: int
    domains: List[Domain]
    accession: str
    sequence: str
    holes: List[Hole] = field(default_factory=list)
    domain_map: Dict[str, List[Domain]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize domain_map and holes after object creation."""
        self._build_domain_map()
        self._identify_holes()
        logger.info(f"System {self.sys_id} initialized with {len(self.domains)} domains and {len(self.holes)} holes")
        logger.info(f"Domains: {self.domains}")
        logger.info(f"Holes: {self.holes}")
    
    def _build_domain_map(self):
        """Build mapping of domain IDs to Domain objects."""
        for domain in self.domains:
            if domain.type != "hole":
                if domain.dom_id not in self.domain_map:
                    self.domain_map[domain.dom_id] = []
                self.domain_map[domain.dom_id].append(domain)
    
    def _identify_holes(self, threshold: int = 50, margin: int = 10):
        """
        Identify inter-domain regions (holes) in the protein sequence.
        
        Args:
            threshold: Minimum hole length to consider
            margin: Margin around domains to exclude from holes
        """
        try:
            # Sort domains by start position
            sorted_domains = sorted(self.domains, key=lambda x: x.start)
            
            # Find gaps between domains
            holes = []
            for i in range(len(sorted_domains) - 1):
                current_domain = sorted_domains[i]
                next_domain = sorted_domains[i + 1]
                
                # Calculate gap
                gap_start = current_domain.end + margin
                gap_end = next_domain.start - margin
                
                if gap_end > gap_start and (gap_end - gap_start + 1) >= threshold:
                    # Create hole domain
                    logger.debug(f"Creating hole domain: gap_start={gap_start}, gap_end={gap_end}, sys_len={self.sys_len}")
                    
                    if self.sys_len <= 0:
                        logger.warning(f"System {self.sys_id}: sys_len={self.sys_len} <= 0, using coverage=0.0")
                        coverage = 0.0
                    else:
                        coverage = (gap_end - gap_start + 1) / self.sys_len
                        logger.debug(f"Hole domain coverage calculation: {coverage}")
                        
                        # Clamp coverage to valid range
                        if coverage < 0 or coverage > 1:
                            logger.warning(f"Hole domain coverage {coverage} outside [0,1] range, clamping")
                            coverage = max(0.0, min(1.0, coverage))
                    
                    hole_domain = Domain(
                        dom_id="-1",
                        start=gap_start,
                        end=gap_end,
                        bitscore=-1,
                        coverage=coverage,
                        type="hole"
                    )
                    
                    # Create hole object
                    hole = Hole(
                        sys_id=self.sys_id,
                        pos=len(holes),
                        names=[],
                        ref_doms=[(current_domain, next_domain)],
                        start=gap_start,
                        end=gap_end,
                        sequence=self.sequence[gap_start-1:gap_end] if gap_start <= len(self.sequence) else ""
                    )
                    holes.append(hole)
                    
                    # Add hole domain to domains list for visualization
                    self.domains.append(hole_domain)
            
            self.holes = holes
        except Exception as e:
            logger.error(f"Error identifying holes for system {self.sys_id}: {e}")
            self.holes = []
    
    def check_characteristic_domains(self, char_domains: List[str]) -> bool:
        """
        Check if system contains characteristic domains.
        
        Args:
            char_domains: List of domain IDs considered characteristic
            
        Returns:
            True if system contains any characteristic domains
        """
        for domain in self.domains:
            if domain.dom_id in char_domains:
                return True
        return False
    
    def get_domain_list(self) -> List[tuple]:
        """Convert domains to list format for compatibility."""
        return [domain.to_tuple() for domain in self.domains]
    
    def get_hole_list(self) -> List[tuple]:
        """Convert holes to list format for compatibility."""
        return [hole.to_tuple() for hole in self.holes]
    
    def generate_csv_row(self) -> List[str]:
        """
        Generate CSV row for this system.
        
        Returns:
            List containing system data for CSV export in the format:
            Accession,Length,Family,Subfamily,Domains,Separators
        """
        # Format domains as list of tuples: (domain_id, start, end, evalue)
        domain_tuples = []
        for domain in self.domains:
            if domain.type != "hole":  # Only include actual domains, not holes
                domain_tuples.append((domain.dom_id, domain.start, domain.end, domain.evalue))
        
        # Format separators (holes) as list of tuples: (description, start, end)
        separator_tuples = []
        print("--------------------------------")
        print(self.sys_id)
        print(self.holes)
        for hole in self.holes:
            separator_tuples.append((hole.best_name, hole.start, hole.end)) 
        
        # Convert to string representation
        domains_str = str(domain_tuples) if domain_tuples else "[]"
        separators_str = str(separator_tuples) if separator_tuples else "[]"
        
        return [
            self.accession,
            str(self.sys_len),
            self.fam_id,
            self.sys_id,  # Using sys_id as subfamily
            domains_str,
            separators_str
        ]
    
    def __repr__(self) -> str:
        return f"System(fam_id='{self.fam_id}', sys_id='{self.sys_id}', domains={len(self.domains)})"
    
    def __str__(self) -> str:
        return f"{self.fam_id}:{self.sys_id} ({len(self.domains)} domains)"
    
    def fill_holes(self):
        """
        Fill gaps between domains with hole domains.
        """
        # Filter out existing holes and sort domains by start position
        non_hole_domains = [dom for dom in self.domains if dom.type != "hole"]
        sorted_domains = sorted(non_hole_domains, key=lambda x: x.start)
        
        # Create a new list for all domains including holes
        new_domains = []
        
        # Check for gap at the beginning
        if not sorted_domains or sorted_domains[0].start > 0:
            start = 0
            end = sorted_domains[0].start - 1 if sorted_domains else self.sys_len - 1
            coverage = (end - start) / self.sys_len if self.sys_len > 0 else 0.0
            hole = Domain("-1", start, end, -1, coverage, type="hole")
            new_domains.append(hole)
        
        # Add first domain
        if sorted_domains:
            new_domains.append(sorted_domains[0])
        
        # Check for gaps between domains
        for i in range(1, len(sorted_domains)):
            prev_end = sorted_domains[i-1].end
            curr_start = sorted_domains[i].start
            
            # If there's a gap between the domains
            if prev_end + 1 < curr_start:
                coverage = (curr_start - prev_end - 1) / self.sys_len if self.sys_len > 0 else 0.0
                hole = Domain("-1", prev_end + 1, curr_start - 1, -1, coverage, type="hole")
                new_domains.append(hole)
            
            # Add current domain
            new_domains.append(sorted_domains[i])
        
        # Check for gap at the end
        if sorted_domains and sorted_domains[-1].end < self.sys_len - 1:
            start = sorted_domains[-1].end + 1
            end = self.sys_len - 1
            coverage = (end - start) / self.sys_len if self.sys_len > 0 else 0.0
            hole = Domain("-1", start, end, -1, coverage, type="hole")
            new_domains.append(hole)
        
        # Update domains
        self.domains = new_domains
        # Rebuild domain map after adding holes
        self._build_domain_map()
    
    def get_holes(self, thresh=50, margin=10):
        """
        Identifies inter-domain regions ("holes") in the system.

        Analyzes the protein sequence to find regions between domains that are
        longer than the threshold length. For each hole, identifies the flanking
        domains within the specified margin.

        Args:
            thresh (int, optional): Minimum length for a region to be considered a hole. 
                                  Defaults to 50.
            margin (int, optional): Number of positions to look for flanking domains. 
                                  Defaults to 10.
        """
        from ..utils.file_utils import find_margins
        
        self.holes = []
        for i, dom in enumerate(self.domains):
            if dom.type == "hole" and dom.end - dom.start >= thresh:
                # Find domains within margin distance of hole boundaries
                left_doms, right_doms = find_margins(self.domains, 
                                                   dom.start - margin, 
                                                   dom.end + margin)
                ref_doms = []
                names = set()

                # Handle cases based on presence of flanking domains
                if len(left_doms) == 0:
                    for rdom in right_doms:
                        names.add((None, rdom.dom_id))
                        ref_doms.append((None, rdom))
                elif len(right_doms) == 0:
                    for ldom in left_doms:
                        names.add((ldom.dom_id, None))
                        ref_doms.append((ldom, None))
                else:
                    for ldom in left_doms:
                        for rdom in right_doms:
                            names.add((ldom.dom_id, rdom.dom_id))
                            ref_doms.append((ldom, rdom))

                # Create new Hole object
                # Convert names set to list of strings for compatibility
                names_list = [f"{left}-{right}" if left and right else f"{left or 'BEGIN'}-{right or 'END'}" 
                             for left, right in names]
                self.holes.append(Hole(self.sys_id.split('-')[0], i, names_list, 
                                     ref_doms, dom.start, dom.end, 
                                     self.sequence[dom.start - 1: dom.end])) 