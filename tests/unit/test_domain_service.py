"""
Unit tests for the DomainService class.
"""

import pytest
from src.services.domain_service import DomainService
from src.core.domain import Domain


class TestDomainService:
    """Test cases for the DomainService class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = DomainService()
    
    def test_merge_overlapping_domains(self):
        """Test merging overlapping domains."""
        domains = [
            Domain(dom_id="A", start=1, end=50, bitscore=10, coverage=0.1),
            Domain(dom_id="A", start=45, end=80, bitscore=15, coverage=0.15),
            Domain(dom_id="B", start=100, end=150, bitscore=20, coverage=0.2),
        ]
        
        merged = self.service.merge_overlapping_domains(domains)
        
        # Should have 2 domains after merging (A domains merged, B separate)
        assert len(merged) == 2
        
        # Check that A domains were merged
        a_domains = [d for d in merged if d.dom_id == "A"]
        assert len(a_domains) == 1
        assert a_domains[0].start == 1
        assert a_domains[0].end == 80  # Merged to cover both ranges
        
        # Check that B domain is unchanged
        b_domains = [d for d in merged if d.dom_id == "B"]
        assert len(b_domains) == 1
        assert b_domains[0].start == 100
        assert b_domains[0].end == 150
    
    def test_merge_overlapping_domains_no_overlap(self):
        """Test merging domains with no overlap."""
        domains = [
            Domain(dom_id="A", start=1, end=50, bitscore=10, coverage=0.1),
            Domain(dom_id="B", start=100, end=150, bitscore=20, coverage=0.2),
        ]
        
        merged = self.service.merge_overlapping_domains(domains)
        
        # Should have same number of domains (no overlap to merge)
        assert len(merged) == 2
        assert merged[0].dom_id == "A"
        assert merged[1].dom_id == "B"
    
    def test_merge_overlapping_domains_empty(self):
        """Test merging empty domain list."""
        merged = self.service.merge_overlapping_domains([])
        assert len(merged) == 0
    
    def test_find_inter_domain_regions(self):
        """Test finding inter-domain regions (holes)."""
        domains = [
            Domain(dom_id="A", start=1, end=50, bitscore=10, coverage=0.1),
            Domain(dom_id="B", start=100, end=150, bitscore=20, coverage=0.2),
        ]
        protein_length = 200
        
        holes = self.service.find_inter_domain_regions(domains, protein_length)
        
        # Should find holes at positions 51-99 and 151-200
        assert len(holes) == 2
        
        # First hole: between domains A and B
        assert holes[0].start == 51
        assert holes[0].end == 99
        assert holes[0].is_hole
        
        # Second hole: after domain B
        assert holes[1].start == 151
        assert holes[1].end == 200
        assert holes[1].is_hole
    
    def test_find_inter_domain_regions_no_gaps(self):
        """Test finding holes when domains are adjacent."""
        domains = [
            Domain(dom_id="A", start=1, end=50, bitscore=10, coverage=0.1),
            Domain(dom_id="B", start=51, end=100, bitscore=20, coverage=0.2),
        ]
        protein_length = 100
        
        holes = self.service.find_inter_domain_regions(domains, protein_length)
        
        # Should find no holes (domains are adjacent)
        assert len(holes) == 0
    
    def test_analyze_domain_composition(self):
        """Test analyzing domain composition."""
        domains = [
            Domain(dom_id="A", start=1, end=50, bitscore=10, coverage=0.1),
            Domain(dom_id="B", start=51, end=100, bitscore=20, coverage=0.2),
            Domain(dom_id="A", start=101, end=150, bitscore=15, coverage=0.15),
        ]
        
        analysis = self.service.analyze_domain_composition(domains)
        
        assert analysis['total_domains'] == 3
        assert analysis['total_holes'] == 0
        assert analysis['coverage'] == pytest.approx(0.45)  # 0.1 + 0.2 + 0.15
        assert analysis['domain_types']['A'] == 2
        assert analysis['domain_types']['B'] == 1
        assert len(analysis['domain_lengths']) == 3
        assert len(analysis['hole_lengths']) == 0
    
    def test_analyze_domain_composition_with_holes(self):
        """Test analyzing domain composition with holes."""
        domains = [
            Domain(dom_id="A", start=1, end=50, bitscore=10, coverage=0.1),
            Domain(dom_id="-1", start=51, end=100, bitscore=-1, coverage=0.1, type="hole"),
            Domain(dom_id="B", start=101, end=150, bitscore=20, coverage=0.2),
        ]
        
        analysis = self.service.analyze_domain_composition(domains)
        
        assert analysis['total_domains'] == 2
        assert analysis['total_holes'] == 1
        assert analysis['coverage'] == pytest.approx(0.3)  # 0.1 + 0.2 (holes don't count)
        assert analysis['domain_types']['A'] == 1
        assert analysis['domain_types']['B'] == 1
        assert len(analysis['domain_lengths']) == 2
        assert len(analysis['hole_lengths']) == 1
    
    def test_get_domain_statistics(self):
        """Test getting domain statistics."""
        domains = [
            Domain(dom_id="A", start=1, end=50, bitscore=10, coverage=0.1),
            Domain(dom_id="B", start=51, end=100, bitscore=20, coverage=0.2),
            Domain(dom_id="A", start=101, end=150, bitscore=15, coverage=0.15),
        ]
        
        stats = self.service.get_domain_statistics(domains)
        
        assert stats['count'] == 3
        assert stats['avg_length'] == 50  # (50 + 50 + 50) / 3
        assert stats['min_length'] == 50
        assert stats['max_length'] == 50
        assert stats['total_coverage'] == pytest.approx(0.45)  # 0.1 + 0.2 + 0.15
    
    def test_get_domain_statistics_empty(self):
        """Test getting statistics for empty domain list."""
        stats = self.service.get_domain_statistics([])
        
        assert stats['count'] == 0
        assert stats['avg_length'] == 0
        assert stats['min_length'] == 0
        assert stats['max_length'] == 0
        assert stats['total_coverage'] == 0
    
    def test_filter_domains_by_score(self):
        """Test filtering domains by minimum score."""
        domains = [
            Domain(dom_id="A", start=1, end=50, bitscore=10, coverage=0.1),
            Domain(dom_id="B", start=51, end=100, bitscore=20, coverage=0.2),
            Domain(dom_id="C", start=101, end=150, bitscore=5, coverage=0.15),
        ]
        
        filtered = self.service.filter_domains_by_score(domains, min_score=15)
        
        assert len(filtered) == 1
        assert filtered[0].dom_id == "B"
        assert filtered[0].bitscore == 20
    
    def test_sort_domains_by_position(self):
        """Test sorting domains by start position."""
        domains = [
            Domain(dom_id="B", start=51, end=100, bitscore=20, coverage=0.2),
            Domain(dom_id="A", start=1, end=50, bitscore=10, coverage=0.1),
            Domain(dom_id="C", start=101, end=150, bitscore=15, coverage=0.15),
        ]
        
        sorted_domains = self.service.sort_domains_by_position(domains)
        
        assert len(sorted_domains) == 3
        assert sorted_domains[0].dom_id == "A"  # start=1
        assert sorted_domains[1].dom_id == "B"  # start=51
        assert sorted_domains[2].dom_id == "C"  # start=101
    
    def test_get_domain_overlaps(self):
        """Test finding overlapping domains."""
        domains = [
            Domain(dom_id="A", start=1, end=50, bitscore=10, coverage=0.1),
            Domain(dom_id="B", start=40, end=100, bitscore=20, coverage=0.2),
            Domain(dom_id="C", start=150, end=200, bitscore=15, coverage=0.15),
        ]
        
        overlaps = self.service.get_domain_overlaps(domains)
        
        # Should find overlap between A and B
        assert len(overlaps) == 1
        overlap_pair = overlaps[0]
        assert overlap_pair[0].dom_id == "A"
        assert overlap_pair[1].dom_id == "B" 