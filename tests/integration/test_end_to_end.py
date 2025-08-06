"""
Integration tests for end-to-end workflow.
"""

import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.cli.main import main
from src.services.family_service import FamilyService
from src.services.visualization_service import VisualizationService
from src.core.family import Family
from src.core.system import System
from src.core.domain import Domain


class TestEndToEndWorkflow:
    """Test cases for end-to-end workflow."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_output_dir = Path("/tmp/test_output")
        self.test_output_dir.mkdir(exist_ok=True)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if self.test_output_dir.exists():
            shutil.rmtree(self.test_output_dir)
    
    @patch('src.cli.main.FamilyService')
    @patch('src.cli.main.VisualizationService')
    @patch('os.path.isfile', return_value=True)
    @patch('os.path.isdir', return_value=True)
    def test_end_to_end_cdd_processing(self, mock_isdir, mock_isfile, mock_viz_service, mock_family_service):
        """Test complete workflow with CDD input."""
        # Mock the services
        mock_family_svc = MagicMock()
        mock_viz_svc = MagicMock()
        mock_family_service.return_value = mock_family_svc
        mock_viz_service.return_value = mock_viz_svc
        
        # Mock family data
        family_data = pd.DataFrame({
            'family': ['1.A.1', '1.A.1'],
            'system': ['sys1', 'sys2'],
            'accession': ['P00001', 'P00002'],
            'domains': ['A:1-50;B:51-100', 'A:1-60']
        })
        
        # Mock family object
        mock_family = MagicMock(spec=Family)
        mock_family.family_id = "1.A.1"
        mock_family.systems = [MagicMock(), MagicMock()]
        
        # Set up service mocks
        mock_family_svc.load_family_data.return_value = family_data
        mock_family_svc.create_family.return_value = mock_family
        mock_family_svc.generate_csv_data.return_value = [['P00001', '100', '1.A.1', 'sys1', 'A:1-50;B:51-100']]
        
        # Mock command line arguments
        with patch('sys.argv', ['script', '-c', 'test.cdd', '-p', 'general', '-o', str(self.test_output_dir)]):
            # Run the main function
            main()
            
            # Verify service calls
            mock_family_svc.load_family_data.assert_called_once()
            mock_family_svc.create_family.assert_called_once()
            mock_viz_svc.generate_plots.assert_called_once()
    
    @patch('src.cli.main.FamilyService')
    @patch('src.cli.main.VisualizationService')
    @patch('os.path.isfile', return_value=True)
    @patch('os.path.isdir', return_value=True)
    def test_end_to_end_rescue_processing(self, mock_isdir, mock_isfile, mock_viz_service, mock_family_service):
        """Test complete workflow with rescue input."""
        # Mock the services
        mock_family_svc = MagicMock()
        mock_viz_svc = MagicMock()
        mock_family_service.return_value = mock_family_svc
        mock_viz_service.return_value = mock_viz_svc
        
        # Mock family data
        family_data = pd.DataFrame({
            'family': ['1.A.1', '1.A.1'],
            'system': ['sys1', 'sys2'],
            'accession': ['P00001', 'P00002'],
            'domains': ['A:1-50;B:51-100', 'A:1-60']
        })
        
        # Mock family object
        mock_family = MagicMock(spec=Family)
        mock_family.family_id = "1.A.1"
        mock_family.systems = [MagicMock(), MagicMock()]
        
        # Set up service mocks
        mock_family_svc.load_family_data.return_value = family_data
        mock_family_svc.create_family.return_value = mock_family
        
        # Mock command line arguments
        with patch('sys.argv', ['script', '-r', 'rescue_dir', '-p', 'char_rescue', '-o', str(self.test_output_dir)]):
            # Run the main function
            main()
            
            # Verify service calls
            mock_family_svc.load_family_data.assert_called_once()
            mock_family_svc.create_family.assert_called_once()
            mock_viz_svc.generate_plots.assert_called_once()
    
    def test_family_service_integration(self):
        """Test integration between family service components."""
        service = FamilyService()
        
        # Create test data
        family_data = pd.DataFrame({
            'family': ['1.A.1', '1.A.1'],
            'system': ['sys1', 'sys2'],
            'accession': ['P00001', 'P00002'],
            'domains': ['A:1-50;B:51-100', 'A:1-60']
        })
        
        # Mock sequence reading
        with patch('src.services.family_service.read_sequence_file') as mock_read_seq:
            mock_read_seq.return_value = {
                'sys1': 'M' * 100,
                'sys2': 'M' * 100
            }
            
            # Test family creation
            family = service.create_family(
                family_data, '1.A.1', str(self.test_output_dir), True
            )
            
            assert isinstance(family, Family)
            assert family.family_id == '1.A.1'
            assert len(family.systems) == 2
    
    def test_visualization_service_integration(self):
        """Test integration between visualization service components."""
        service = VisualizationService()
        
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
            output_directory=self.test_output_dir
        )
        
        # Mock the visualization methods
        with patch.object(service.family_visualizer, 'plot_domain_architecture') as mock_general:
            service.generate_plots(family, ["general"])
            mock_general.assert_called_once_with(family)
    
    def test_data_export_integration(self):
        """Test integration of data export functionality."""
        service = FamilyService()
        
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
            output_directory=self.test_output_dir
        )
        
        # Test CSV generation
        csv_data = service.generate_csv_data(family)
        assert len(csv_data) == 1
        assert csv_data[0][0] == 'P00001'  # accession
        assert csv_data[0][2] == '1.A.1'   # family
        assert csv_data[0][3] == 'sys1'    # system
        assert "('A', 1, 50," in csv_data[0][4]  # domains
    
    def test_error_handling_integration(self):
        """Test error handling in the integrated workflow."""
        service = FamilyService()
        
        # Test with invalid family data
        invalid_data = pd.DataFrame({
            'family': ['1.A.1'],
            'system': ['sys1'],
            'accession': ['P00001'],
            'domains': ['invalid_domain_format']
        })
        
        with patch('src.services.family_service.read_sequence_file') as mock_read_seq:
            mock_read_seq.return_value = {'sys1': 'M' * 100}
            
            # Should handle invalid domain format gracefully
            family = service.create_family(
                invalid_data, '1.A.1', str(self.test_output_dir), True
            )
            
            assert isinstance(family, Family)
            # The family should be created but with empty domains
            assert len(family.systems) == 1 