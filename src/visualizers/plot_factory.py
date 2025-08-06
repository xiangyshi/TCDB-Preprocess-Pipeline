"""
Plot factory for TCDB Domain Visualization.

This module provides a factory pattern for creating different types of plots
and visualizations.
"""

from typing import Dict, Type, Any
from .domain_visualizer import DomainVisualizer
from .family_visualizer import FamilyVisualizer
from ..core.family import Family


class PlotFactory:
    """
    Factory for creating different types of plots and visualizations.
    """
    
    def __init__(self):
        """Initialize the plot factory."""
        self.domain_visualizer = DomainVisualizer()
        self.family_visualizer = FamilyVisualizer()
        
        # Register plot types
        self._register_plot_types()
    
    def _register_plot_types(self):
        """Register available plot types."""
        self.plot_types = {
            'general': self._create_general_plots,
            'char': self._create_characteristic_plots,
            'arch': self._create_architecture_plots,
            'holes': self._create_hole_plots,
            'summary': self._create_summary_plots,
            'char_rescue': self._create_rescue_plots
        }
    
    def create_plot(self, plot_type: str, family: Family, **kwargs) -> Any:
        """
        Create a plot of the specified type.
        
        Args:
            plot_type: Type of plot to create
            family: Family object to visualize
            **kwargs: Additional arguments for plot creation
            
        Returns:
            Plot object or None if plot type not supported
        """
        if plot_type not in self.plot_types:
            raise ValueError(f"Unknown plot type: {plot_type}")
        
        return self.plot_types[plot_type](family, **kwargs)
    
    def create_all_plots(self, family: Family) -> Dict[str, Any]:
        """
        Create all available plot types for a family.
        
        Args:
            family: Family object to visualize
            
        Returns:
            Dictionary mapping plot types to plot objects
        """
        plots = {}
        
        for plot_type in self.plot_types:
            try:
                plots[plot_type] = self.create_plot(plot_type, family)
            except Exception as e:
                print(f"Error creating {plot_type} plot: {e}")
                plots[plot_type] = None
        
        return plots
    
    def _create_general_plots(self, family: Family, **kwargs) -> None:
        """Create general domain plots."""
        self.domain_visualizer.plot_general_domains(family)
        self.domain_visualizer.plot_domain_frequency(family)
        self.domain_visualizer.plot_domain_coverage(family)
    
    def _create_characteristic_plots(self, family: Family, **kwargs) -> None:
        """Create characteristic domain plots."""
        self.domain_visualizer.plot_characteristic_domains(family)
    
    def _create_architecture_plots(self, family: Family, **kwargs) -> None:
        """Create domain architecture plots."""
        self.family_visualizer.plot_domain_architecture(family)
    
    def _create_hole_plots(self, family: Family, **kwargs) -> None:
        """Create hole analysis plots."""
        self.family_visualizer.plot_holes(family)
    
    def _create_summary_plots(self, family: Family, **kwargs) -> None:
        """Create summary statistics plots."""
        self.family_visualizer.plot_summary_statistics(family)
    
    def _create_rescue_plots(self, family: Family, **kwargs) -> None:
        """Create rescue-specific plots."""
        self.domain_visualizer.plot_rescue_characteristics(family)
    
    def get_available_plot_types(self) -> list:
        """
        Get list of available plot types.
        
        Returns:
            List of available plot types
        """
        return list(self.plot_types.keys())
    
    def get_plot_description(self, plot_type: str) -> str:
        """
        Get description of a plot type.
        
        Args:
            plot_type: Type of plot
            
        Returns:
            Description of the plot type
        """
        descriptions = {
            'general': 'General domain distribution and frequency plots',
            'char': 'Characteristic domain analysis plots',
            'arch': 'Domain architecture visualizations',
            'holes': 'Inter-domain region (hole) analysis',
            'summary': 'Summary statistics and overview plots',
            'char_rescue': 'Rescue-specific characteristic plots'
        }
        
        return descriptions.get(plot_type, 'Unknown plot type')
    
    def validate_plot_type(self, plot_type: str) -> bool:
        """
        Validate if a plot type is supported.
        
        Args:
            plot_type: Type of plot to validate
            
        Returns:
            True if plot type is supported
        """
        return plot_type in self.plot_types
    
    def create_custom_plot(self, plot_type: str, family: Family, custom_params: Dict) -> Any:
        """
        Create a custom plot with specific parameters.
        
        Args:
            plot_type: Type of plot to create
            family: Family object to visualize
            custom_params: Custom parameters for plot creation
            
        Returns:
            Plot object or None if creation fails
        """
        try:
            if plot_type == 'general':
                return self._create_custom_general_plot(family, custom_params)
            elif plot_type == 'summary':
                return self._create_custom_summary_plot(family, custom_params)
            else:
                return self.create_plot(plot_type, family)
        except Exception as e:
            print(f"Error creating custom {plot_type} plot: {e}")
            return None
    
    def _create_custom_general_plot(self, family: Family, params: Dict) -> None:
        """Create custom general plot with specific parameters."""
        # Implementation for custom general plots
        pass
    
    def _create_custom_summary_plot(self, family: Family, params: Dict) -> None:
        """Create custom summary plot with specific parameters."""
        # Implementation for custom summary plots
        pass 