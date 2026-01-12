"""
Unit tests for the Domain class.

This module contains unit tests for the Domain entity.
"""

import pytest
from src.core.domain import Domain, create_hole


class TestDomain:
    """Test cases for the Domain class."""
    
    def test_domain_creation(self):
        """Test basic domain creation."""
        domain = Domain(
            dom_id="test_domain",
            start=1,
            end=100,
            bitscore=50.0,
            coverage=0.5
        )
        
        assert domain.dom_id == "test_domain"
        assert domain.start == 1
        assert domain.end == 100
        assert domain.bitscore == 50.0
        assert domain.coverage == 0.5
        assert domain.type == "domain"
        assert domain.length == 100
    
    def test_domain_validation(self):
        """Test domain validation."""
        # Test invalid start position
        with pytest.raises(ValueError, match="Start position must be 0 or greater"):
            Domain(dom_id="test", start=-1, end=100, bitscore=50.0, coverage=0.5)
        
        # Test invalid end position
        with pytest.raises(ValueError, match="End position must be greater than or equal to start position"):
            Domain(dom_id="test", start=100, end=50, bitscore=50.0, coverage=0.5)
        
        # Test invalid coverage
        with pytest.raises(ValueError, match="Coverage must be between 0 and 1"):
            Domain(dom_id="test", start=1, end=100, bitscore=50.0, coverage=1.5)
        
        # Test invalid type
        with pytest.raises(ValueError, match="Type must be 'domain' or 'hole'"):
            Domain(dom_id="test", start=1, end=100, bitscore=50.0, coverage=0.5, type="invalid")
    
    def test_domain_properties(self):
        """Test domain properties."""
        domain = Domain(
            dom_id="test_domain",
            start=10,
            end=50,
            bitscore=75.0,
            coverage=0.4
        )
        
        assert domain.length == 41  # 50 - 10 + 1
        assert not domain.is_hole
    
    def test_hole_domain(self):
        """Test hole domain creation."""
        domain = Domain(
            dom_id="-1",
            start=1,
            end=100,
            bitscore=-1,
            coverage=0.5,
            type="hole"
        )
        
        assert domain.is_hole
        assert domain.type == "hole"
    
    def test_domain_overlap(self):
        """Test domain overlap detection."""
        domain1 = Domain(dom_id="test1", start=1, end=100, bitscore=50.0, coverage=0.5)
        domain2 = Domain(dom_id="test2", start=50, end=150, bitscore=60.0, coverage=0.6)
        domain3 = Domain(dom_id="test3", start=200, end=300, bitscore=70.0, coverage=0.7)
        
        # Test overlapping domains
        assert domain1.overlaps_with(domain2)
        assert domain2.overlaps_with(domain1)
        
        # Test non-overlapping domains
        assert not domain1.overlaps_with(domain3)
        assert not domain3.overlaps_with(domain1)
    
    def test_domain_to_tuple(self):
        """Test domain to tuple conversion."""
        domain = Domain(
            dom_id="test_domain",
            start=1,
            end=100,
            bitscore=50.0,
            coverage=0.5,
            evalue=1e-10
        )
        
        expected_tuple = ("test_domain", 1, 100, 1e-10)
        assert domain.to_tuple() == expected_tuple
    
    def test_domain_repr(self):
        """Test domain string representation."""
        domain = Domain(
            dom_id="test_domain",
            start=1,
            end=100,
            bitscore=50.0,
            coverage=0.5
        )
        
        expected_repr = "Domain(id='test_domain', start=1, end=100, type='domain')"
        assert repr(domain) == expected_repr
    
    def test_domain_str(self):
        """Test domain string conversion."""
        domain = Domain(
            dom_id="test_domain",
            start=1,
            end=100,
            bitscore=50.0,
            coverage=0.5
        )
        
        expected_str = "test_domain:1-100"
        assert str(domain) == expected_str


class TestCreateHole:
    """Test cases for the create_hole function."""
    
    def test_create_hole(self):
        """Test hole creation."""
        hole = create_hole(start=50, end=100, protein_length=500)
        
        assert hole.dom_id == "-1"
        assert hole.start == 50
        assert hole.end == 100
        assert hole.bitscore == -1
        assert hole.type == "hole"
        assert hole.coverage == 0.102  # (100 - 50 + 1) / 500
        assert hole.is_hole 