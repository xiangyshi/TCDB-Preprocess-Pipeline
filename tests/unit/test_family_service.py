"""
Unit tests for the FamilyService class.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from src.services.family_service import FamilyService
from src.core.family import Family
from src.core.system import System
from src.core.domain import Domain


class TestFamilyService:
    """Test cases for the FamilyService class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = FamilyService()
    
    def test_load_family_data_cdd(self):
        """Test loading family data from CDD file."""
        with patch.object(self.service.cdd_parser, 'parse_file') as mock_parse:
            mock_parse.return_value = pd.DataFrame({
                'family': ['1.A.1', '1.A.1'],
                'system': ['sys1', 'sys2'],
                'accession': ['P00001', 'P00002'],
                'domains': ['A:1-50;B:51-100', 'A:1-60']
            })
            
            result = self.service.load_family_data('test.cdd', 'cdd', '1.A.1')
            
            mock_parse.assert_called_once_with('test.cdd', '1.A.1')
            assert len(result) == 2
            assert result.iloc[0]['family'] == '1.A.1'
    
    def test_load_family_data_rescue(self):
        """Test loading family data from rescue directory."""
        with patch.object(self.service.rescue_parser, 'parse_directory') as mock_parse:
            mock_parse.return_value = pd.DataFrame({
                'family': ['1.A.1', '1.A.1'],
                'system': ['sys1', 'sys2'],
                'accession': ['P00001', 'P00002'],
                'domains': ['A:1-50;B:51-100', 'A:1-60']
            })
            
            result = self.service.load_family_data('rescue_dir', 'rescue', '1.A.1')
            
            mock_parse.assert_called_once_with('rescue_dir', '1.A.1')
            assert len(result) == 2
    
    def test_load_family_data_invalid_type(self):
        """Test loading family data with invalid input type."""
        with pytest.raises(ValueError, match="Unsupported input type"):
            self.service.load_family_data('test', 'invalid', None)
    
    @patch('src.services.family_service.read_sequence_file')
    def test_create_family(self, mock_read_sequence):
        """Test creating a Family object from family data."""
        # Mock sequence file reading
        mock_read_sequence.return_value = {
            'sys1': 'M' * 100,
            'sys2': 'M' * 100
        }
        
        # Create test data
        family_data = pd.DataFrame({
            'family': ['1.A.1', '1.A.1'],
            'system': ['sys1', 'sys2'],
            'accession': ['P00001', 'P00002'],
            'domains': ['A:1-50;B:51-100', 'A:1-60']
        })
        
        with patch('src.services.family_service.config') as mock_config:
            mock_config.get_sequence_file_path.return_value = 'test.faa'
            
            family = self.service.create_family(
                family_data, '1.A.1', '/tmp/output', True
            )
            
            assert isinstance(family, Family)
            assert family.family_id == '1.A.1'
            assert len(family.systems) == 2
            assert family.merge_overlapping is True
    
    def test_get_characteristic_domains(self):
        """Test getting characteristic domains for a family."""
        # Create a test family
        systems = [
            System(
                fam_id="1.A.1",
                sys_id="sys1",
                sys_len=100,
                domains=[
                    Domain(dom_id="A", start=1, end=50, bitscore=10, coverage=0.5),
                    Domain(dom_id="B", start=51, end=100, bitscore=20, coverage=0.5),
                ],
                accession="P00001",
                sequence="M"*100
            ),
            System(
                fam_id="1.A.1",
                sys_id="sys2",
                sys_len=100,
                domains=[
                    Domain(dom_id="A", start=1, end=60, bitscore=15, coverage=0.6),
                ],
                accession="P00002",
                sequence="M"*100
            ),
        ]
        
        family = Family(
            family_id="1.A.1",
            systems=systems,
            output_directory=Path("/tmp")
        )
        
        # Test with default threshold (0.5)
        char_domains = self.service.get_characteristic_domains(family)
        assert "A" in char_domains  # Appears in both systems
        assert "B" not in char_domains  # Appears in 1/2 systems = 50% (not > 50%)
        
        # Test with higher threshold (0.6)
        char_domains = self.service.get_characteristic_domains(family, threshold=0.6)
        assert "A" in char_domains  # Appears in both systems
        assert "B" not in char_domains  # 50% < 60%
    
    def test_analyze_family_statistics(self):
        """Test analyzing family statistics."""
        # Create a test family
        systems = [
            System(
                fam_id="1.A.1",
                sys_id="sys1",
                sys_len=100,
                domains=[
                    Domain(dom_id="A", start=1, end=50, bitscore=10, coverage=0.5),
                ],
                accession="P00001",
                sequence="M"*100
            ),
            System(
                fam_id="1.A.1",
                sys_id="sys2",
                sys_len=200,
                domains=[
                    Domain(dom_id="A", start=1, end=60, bitscore=15, coverage=0.6),
                ],
                accession="P00002",
                sequence="M"*200
            ),
        ]
        
        family = Family(
            family_id="1.A.1",
            systems=systems,
            output_directory=Path("/tmp")
        )
        
        stats = self.service.analyze_family_statistics(family)
        
        assert stats['family_id'] == '1.A.1'
        assert stats['num_systems'] == 2
        assert stats['avg_protein_length'] == 150  # (100 + 200) / 2
        assert stats['total_domains'] == 2
        assert stats['unique_domains'] == ['A']
        assert stats['domain_frequencies']['A'] == 2
    
    def test_generate_csv_data(self):
        """Test generating CSV data for a family."""
        # Create a test family
        systems = [
            System(
                fam_id="1.A.1",
                sys_id="sys1",
                sys_len=100,
                domains=[
                    Domain(dom_id="A", start=1, end=50, bitscore=10, coverage=0.5),
                ],
                accession="P00001",
                sequence="M"*100
            ),
        ]
        
        family = Family(
            family_id="1.A.1",
            systems=systems,
            output_directory=Path("/tmp")
        )
        
        csv_rows = self.service.generate_csv_data(family)
        
        assert len(csv_rows) == 1
        assert csv_rows[0][0] == 'P00001'  # accession
        assert csv_rows[0][2] == '1.A.1'   # family
        assert csv_rows[0][3] == 'sys1'    # system
        assert "('A', 1, 50," in csv_rows[0][4]  # domains 