"""
Domain entity representing a protein domain or inter-domain region.

This module contains the Domain class that represents a protein domain or
inter-domain region ("hole") within a protein sequence.
"""

from dataclasses import dataclass
from typing import Optional, Union
import numpy as np
import logging

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Domain:
    """
    A protein domain or inter-domain region.
    
    Attributes:
        dom_id: Unique identifier for the domain
        start: Start position in protein sequence (1-based)
        end: End position in protein sequence (1-based)
        bitscore: Bitscore from domain alignment
        evalue: E-value from domain alignment (optional)
        coverage: Fraction of protein covered by this domain
        type: Type of region ("domain" or "hole")
        rescue_round: Rescue round information (for rescue data)
    """
    
    dom_id: str
    start: int
    end: int
    bitscore: Union[int, float]
    coverage: float
    evalue: Optional[float] = None
    type: str = "domain"
    rescue_round: Optional[int] = None
    
    def __post_init__(self):
        """Validate domain data after initialization."""
        if self.start < 0:
            raise ValueError("Start position must be 0 or greater")
        if self.end < self.start:
            raise ValueError("End position must be greater than or equal to start position")
        if self.coverage < 0 or self.coverage > 1:
            raise ValueError(f"Coverage must be between 0 and 1: {self.coverage}")
        if self.type not in ["domain", "hole"]:
            raise ValueError("Type must be 'domain' or 'hole'")
    
    @property
    def length(self) -> int:
        """Length of the domain in amino acids."""
        return self.end - self.start + 1
    
    @property
    def is_hole(self) -> bool:
        """Whether this represents an inter-domain region."""
        return self.type == "hole"
    
    def overlaps_with(self, other: 'Domain', threshold: float = 0.2) -> bool:
        """
        Check if this domain overlaps with another domain.
        
        Args:
            other: Another domain to check overlap with
            threshold: Minimum overlap fraction to consider domains overlapping
            
        Returns:
            True if domains overlap by at least the threshold amount
        """
        overlap_start = max(self.start, other.start)
        overlap_end = min(self.end, other.end)
        
        if overlap_end < overlap_start:
            return False
            
        overlap_length = overlap_end - overlap_start + 1
        min_length = min(self.length, other.length)
        
        return overlap_length / min_length >= threshold
    
    def to_tuple(self) -> tuple:
        """Convert domain to tuple format for compatibility."""
        return (self.dom_id, self.start, self.end, self.evalue)
    
    def __repr__(self) -> str:
        return f"Domain(id='{self.dom_id}', start={self.start}, end={self.end}, type='{self.type}')"
    
    def __str__(self) -> str:
        return f"{self.dom_id}:{self.start}-{self.end}"


def create_hole(start: int, end: int, protein_length: int) -> Domain:
    """
    Create a hole (inter-domain region) domain.
    
    Args:
        start: Start position of the hole
        end: End position of the hole
        protein_length: Total length of the protein
        
    Returns:
        A Domain object representing the hole
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.debug(f"create_hole: start={start}, end={end}, protein_length={protein_length}")
    
    # Handle edge cases
    if protein_length <= 0:
        logger.warning(f"create_hole: protein_length={protein_length} <= 0, setting coverage=0.0")
        coverage = 0.0
    else:
        coverage = (end - start + 1) / protein_length
        logger.debug(f"create_hole: calculated coverage={coverage}")
        
        # Clamp coverage to valid range
        if coverage < 0 or coverage > 1:
            logger.warning(f"create_hole: coverage {coverage} outside [0,1] range, clamping")
            coverage = max(0.0, min(1.0, coverage))
    
    logger.debug(f"create_hole: final coverage={coverage}")
    
    return Domain(
        dom_id="-1",
        start=start,
        end=end,
        bitscore=-1,
        coverage=coverage,
        type="hole"
    ) 