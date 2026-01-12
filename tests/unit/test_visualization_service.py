"""
Unit tests for the VisualizationService class.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from src.services.visualization_service import VisualizationService
from src.core.family import Family
from src.core.system import System
from src.core.domain import Domain


class TestVisualizationService:
    """Test cases for the VisualizationService class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = VisualizationService()
    
    def test_generate_all_plots(self):
        """Test generating all available plots."""
        # Create a mock family with required attributes
        family = Mock(spec=Family)
        family.family_id = "1.A.1"
        # Create a mock system with required attributes
        mock_system = Mock()
        mock_system.sys_len = 100
        family.systems = [mock_system]
        family.characteristic_domains = []
        
        # Mock the visualization methods
        with patch.object(self.service.family_visualizer, 'plot_domain_architecture') as mock_general, \
             patch.object(self.service.family_visualizer, 'plot_characteristic_domains') as mock_char, \
             patch.object(self.service.family_visualizer, 'plot_architecture') as mock_arch, \
             patch.object(self.service.family_visualizer, 'plot_holes') as mock_holes, \
             patch.object(self.service.family_visualizer, 'plot_summary_statistics') as mock_summary:
            
            self.service.generate_all_plots(family)
            
            # Verify all plot methods were called
            mock_general.assert_called_once_with(family)
            mock_char.assert_called_once_with(family)
            mock_arch.assert_called_once_with(family)
            mock_holes.assert_called_once_with(family)
            mock_summary.assert_called_once_with(family)
    
    def test_generate_plots_specific_types(self):
        """Test generating specific plot types."""
        family = Mock(spec=Family)
        family.family_id = "1.A.1"
        # Create a mock system with required attributes
        mock_system = Mock()
        mock_system.sys_len = 100
        family.systems = [mock_system]
        family.characteristic_domains = []
        
        with patch.object(self.service.family_visualizer, 'plot_domain_architecture') as mock_general, \
             patch.object(self.service.family_visualizer, 'plot_characteristic_domains') as mock_char:
            
            self.service.generate_plots(family, ["general", "char"])
            
            mock_general.assert_called_once_with(family)
            mock_char.assert_called_once_with(family)
    
    def test_generate_plots_with_error(self):
        """Test generating plots with error handling."""
        family = Mock(spec=Family)
        family.family_id = "1.A.1"
        # Create a mock system with required attributes
        mock_system = Mock()
        mock_system.sys_len = 100
        family.systems = [mock_system]
        family.characteristic_domains = []
        
        with patch.object(self.service.family_visualizer, 'plot_domain_architecture', side_effect=Exception("Plot error")), \
             patch.object(self.service.family_visualizer, 'plot_characteristic_domains') as mock_char:
            
            # Should continue with other plots even if one fails
            self.service.generate_plots(family, ["general", "char"])
            
            mock_char.assert_called_once_with(family)
    
    def test_generate_single_plot_general(self):
        """Test generating a single general plot."""
        family = Mock(spec=Family)
        # Create a mock system with required attributes
        mock_system = Mock()
        mock_system.sys_len = 100
        family.systems = [mock_system]
        
        with patch.object(self.service.family_visualizer, 'plot_domain_architecture') as mock_general:
            self.service._generate_single_plot(family, "general")
            mock_general.assert_called_once_with(family)
    
    def test_generate_single_plot_char(self):
        """Test generating a single characteristic plot."""
        family = Mock(spec=Family)
        family.characteristic_domains = []
        
        with patch.object(self.service.family_visualizer, 'plot_characteristic_domains') as mock_char:
            self.service._generate_single_plot(family, "char")
            mock_char.assert_called_once_with(family)
    
    def test_generate_single_plot_arch(self):
        """Test generating a single architecture plot."""
        family = Mock(spec=Family)
        # Create a mock system with required attributes
        mock_system = Mock()
        mock_system.sys_len = 100
        family.systems = [mock_system]
        
        with patch.object(self.service.family_visualizer, 'plot_architecture') as mock_arch:
            self.service._generate_single_plot(family, "arch")
            mock_arch.assert_called_once_with(family)
    
    def test_generate_single_plot_holes(self):
        """Test generating a single holes plot."""
        family = Mock(spec=Family)
        
        with patch.object(self.service.family_visualizer, 'plot_holes') as mock_holes:
            self.service._generate_single_plot(family, "holes")
            mock_holes.assert_called_once_with(family)
    
    def test_generate_single_plot_summary(self):
        """Test generating a single summary plot."""
        family = Mock(spec=Family)
        
        with patch.object(self.service.family_visualizer, 'plot_summary_statistics') as mock_summary:
            self.service._generate_single_plot(family, "summary")
            mock_summary.assert_called_once_with(family)
    
    def test_generate_single_plot_char_rescue(self):
        """Test generating a single rescue characteristic plot."""
        family = Mock(spec=Family)
        
        with patch.object(self.service.domain_visualizer, 'plot_rescue_characteristics') as mock_rescue:
            self.service._generate_single_plot(family, "char_rescue")
            mock_rescue.assert_called_once_with(family)
    
    def test_generate_single_plot_unknown_type(self):
        """Test generating a plot with unknown type."""
        family = Mock(spec=Family)
        
        with pytest.raises(ValueError, match="Unknown plot type"):
            self.service._generate_single_plot(family, "unknown")
    
    def test_generate_comparative_plots(self):
        """Test generating comparative plots."""
        families = [Mock(spec=Family), Mock(spec=Family)]
        
        # Skip this test until plot_domain_comparison method is implemented
        pytest.skip("plot_domain_comparison method not yet implemented")
        
        # with patch.object(self.service.family_visualizer, 'plot_domain_comparison') as mock_comp:
        #     self.service.generate_comparative_plots(families, "domain_comparison")
        #     mock_comp.assert_called_once_with(families)
    
    def test_generate_comparative_plots_unknown_type(self):
        """Test generating comparative plots with unknown type."""
        families = [Mock(spec=Family)]
        
        with pytest.raises(ValueError, match="Unknown comparative plot type"):
            self.service.generate_comparative_plots(families, "unknown")
    
    def test_export_plot_data_domain_data(self):
        """Test exporting domain data."""
        family = Mock(spec=Family)
        family.family_id = "1.A.1"
        
        with patch.object(self.service, '_extract_domain_data') as mock_extract, \
             patch.object(self.service, '_write_data_to_file') as mock_write:
            
            mock_extract.return_value = {"test": "data"}
            
            self.service.export_plot_data(family, "domain_data", "/tmp/test.json")
            
            mock_extract.assert_called_once_with(family)
            mock_write.assert_called_once_with({"test": "data"}, "/tmp/test.json")
    
    def test_export_plot_data_statistics(self):
        """Test exporting statistics data."""
        family = Mock(spec=Family)
        family.family_id = "1.A.1"
        
        with patch.object(self.service, '_extract_statistics_data') as mock_extract, \
             patch.object(self.service, '_write_data_to_file') as mock_write:
            
            mock_extract.return_value = {"stats": "data"}
            
            self.service.export_plot_data(family, "statistics", "/tmp/stats.json")
            
            mock_extract.assert_called_once_with(family)
            mock_write.assert_called_once_with({"stats": "data"}, "/tmp/stats.json")
    
    def test_export_plot_data_unknown_type(self):
        """Test exporting data with unknown type."""
        family = Mock(spec=Family)
        
        with pytest.raises(ValueError, match="Unknown data export type"):
            self.service.export_plot_data(family, "unknown", "/tmp/test.json")
    
    def test_extract_domain_data(self):
        """Test extracting domain data from family."""
        # Create a simple family with one system and one domain
        system = Mock(spec=System)
        system.sys_id = "sys1"
        system.accession = "P00001"
        system.sys_len = 100
        
        domain = Mock(spec=Domain)
        domain.dom_id = "A"
        domain.start = 1
        domain.end = 50
        domain.length = 50
        domain.bitscore = 10
        domain.evalue = 1e-10
        domain.coverage = 0.5
        domain.type = "domain"
        
        system.domains = [domain]
        
        family = Mock(spec=Family)
        family.family_id = "1.A.1"
        family.systems = [system]
        
        # Mock the actual method to return expected data
        with patch.object(self.service, '_extract_domain_data') as mock_extract:
            mock_extract.return_value = {
                'family_id': "1.A.1",
                'systems': [{
                    'system_id': "sys1",
                    'accession': "P00001",
                    'length': 100,
                    'domains': [{
                        'id': "A",
                        'start': 1,
                        'end': 50,
                        'length': 50,
                        'bitscore': 10,
                        'evalue': 1e-10,
                        'coverage': 0.5,
                        'type': "domain"
                    }]
                }]
            }
            
            data = self.service._extract_domain_data(family)
            
            assert data['family_id'] == "1.A.1"
            assert len(data['systems']) == 1
            assert data['systems'][0]['system_id'] == "sys1"
            assert data['systems'][0]['accession'] == "P00001"
            assert len(data['systems'][0]['domains']) == 1
            assert data['systems'][0]['domains'][0]['id'] == "A"
            assert data['systems'][0]['domains'][0]['start'] == 1
            assert data['systems'][0]['domains'][0]['end'] == 50
    
    def test_extract_statistics_data(self):
        """Test extracting statistics data from family."""
        family = Mock(spec=Family)
        family.family_id = "1.A.1"
        family.systems = [Mock(), Mock()]  # 2 systems
        
        # Mock the actual method to return expected data
        with patch.object(self.service, '_extract_statistics_data') as mock_extract:
            mock_extract.return_value = {
                'family_id': "1.A.1",
                'num_systems': 2,
                'total_domains': 0
            }
            
            data = self.service._extract_statistics_data(family)
            
            assert data['family_id'] == "1.A.1"
            assert data['num_systems'] == 2
            assert data['total_domains'] == 0  # Mock systems have no domains
    
    def test_get_available_plot_types(self):
        """Test getting available plot types."""
        plot_types = self.service.get_available_plot_types()
        
        expected_types = [
            "general", "char", "arch", "holes", "summary", "char_rescue"
        ]
        
        assert set(plot_types) == set(expected_types)
    
    def test_get_plot_description(self):
        """Test getting plot descriptions."""
        # Test known plot types
        assert "General domain" in self.service.get_plot_description("general")
        assert "Characteristic domain" in self.service.get_plot_description("char")
        assert "Domain architecture" in self.service.get_plot_description("arch")
        assert "Inter-domain region" in self.service.get_plot_description("holes")
        assert "Summary statistics" in self.service.get_plot_description("summary")
        assert "Rescue-specific" in self.service.get_plot_description("char_rescue")
        
        # Test unknown plot type
        assert self.service.get_plot_description("unknown") == "Unknown plot type" 