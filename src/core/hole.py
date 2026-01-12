"""
Hole entity representing an inter-domain region between protein domains.

This module contains the Hole class that represents an inter-domain region
("hole") between protein domains.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
from .domain import Domain


@dataclass
class Hole:
    """
    An inter-domain region in a protein sequence.
    
    Attributes:
        sys_id: Identifier of the protein system containing this hole
        pos: Position of the hole in the sequence of holes
        names: List of possible names for this hole
        ref_doms: List of domain pairs that flank this hole
        start: Start position of the hole in the protein sequence
        end: End position of the hole in the protein sequence
        sequence: Amino acid sequence of the hole region
        best_name: Best representative name for the hole based on flanking domains
    """
    
    sys_id: str
    pos: int
    names: List[str]
    ref_doms: List[Tuple[Optional[Domain], Optional[Domain]]]
    start: int
    end: int
    sequence: str
    best_name: Optional[str] = None
    
    def __post_init__(self):
        """Set best_name after initialization if not provided."""
        if self.best_name is None:
            self.best_name = self._get_best_name()
    
    @property
    def length(self) -> int:
        """Length of the hole in amino acids."""
        return self.end - self.start + 1
    
    def _get_best_name(self) -> str:
        """
        Determine the best name for the hole based on its flanking domains.
        
        The name is constructed from the highest scoring domains on either side.
        If no domain exists on either side, "BEGIN" or "END" is used respectively.
        
        Returns:
            Name in format "LEFT_DOMAIN to RIGHT_DOMAIN"
        """
        # Extract left and right domains, filtering out None values
        left_doms = [pair[0] for pair in self.ref_doms if pair[0] is not None]
        right_doms = [pair[1] for pair in self.ref_doms if pair[1] is not None]
        
        # Sort domains by bitscore to get best matches
        left_doms.sort(key=lambda x: x.bitscore, reverse=True)
        right_doms.sort(key=lambda x: x.bitscore, reverse=True)
        
        print(left_doms, right_doms)
        # Default names if no domains found
        left_best = "BEGIN"
        right_best = "END"
        
        # Get highest scoring domain IDs if available
        if left_doms:
            left_best = left_doms[0].dom_id
        if right_doms:
            right_best = right_doms[0].dom_id
        print(left_best, right_best)
        print()
        return f"{left_best} to {right_best}"
    
    def to_tuple(self) -> Tuple[str, int, int]:
        """
        Convert hole information to a tuple format.
        
        Returns:
            Tuple containing (best_name, start, end)
        """
        return (self.best_name, self.start, self.end)
    
    def __repr__(self) -> str:
        return f"Hole(sys_id='{self.sys_id}', start={self.start}, end={self.end}, name='{self.best_name}')"
    
    def __str__(self) -> str:
        return f"{self.sys_id} {self.start}-{self.end} {self.best_name}" 