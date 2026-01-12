"""
Visualization service for TCDB Domain Visualization.

This module contains the business logic for generating plots and visualizations.
"""

from typing import List, Optional
from ..core.family import Family
from ..visualizers.domain_visualizer import DomainVisualizer
from ..visualizers.family_visualizer import FamilyVisualizer
from ..visualizers.plot_factory import PlotFactory


class VisualizationService:
    """
    Service for generating plots and visualizations.
    """
    
    def __init__(self):
        """Initialize the visualization service."""
        self.domain_visualizer = DomainVisualizer()
        self.family_visualizer = FamilyVisualizer()
        self.plot_factory = PlotFactory()
    
    def generate_all_plots(self, family: Family) -> None:
        """
        Generate all available plots for a family.
        
        Args:
            family: Family object to visualize
        """
        plot_types = ["general", "char", "arch", "holes", "summary"]
        self.generate_plots(family, plot_types)
    
    def generate_plots(self, family: Family, plot_types: List[str]) -> None:
        """
        Generate specific plot types for a family.
        
        Args:
            family: Family object to visualize
            plot_types: List of plot types to generate
        """
        for plot_type in plot_types:
            try:
                self._generate_single_plot(family, plot_type)
            except Exception as e:
                # Log error but continue with other plots
                print(f"Error generating {plot_type} plot for family {family.family_id}: {e}")
    
    def _generate_single_plot(self, family: Family, plot_type: str) -> None:
        """
        Generate a single plot for a family.
        
        Args:
            family: Family object to visualize
            plot_type: Type of plot to generate
        """
        if plot_type == "general":
            self.family_visualizer.plot_domain_architecture(family)
        elif plot_type == "char":
            self.family_visualizer.plot_characteristic_domains(family)
        elif plot_type == "arch":
            self.family_visualizer.plot_architecture(family)
        elif plot_type == "holes":
            self.family_visualizer.plot_holes(family)
        elif plot_type == "summary":
            self.family_visualizer.plot_summary_statistics(family)
        elif plot_type == "char_rescue":
            # Check if this is a rescue family and use its specific plotting method
            if hasattr(family, 'plot_characteristic_rescue'):
                family.plot_characteristic_rescue()
            else:
                self.domain_visualizer.plot_rescue_characteristics(family)
        else:
            raise ValueError(f"Unknown plot type: {plot_type}")
    
    def generate_comparative_plots(self, families: List[Family], plot_type: str) -> None:
        """
        Generate comparative plots across multiple families.
        
        Args:
            families: List of family objects to compare
            plot_type: Type of comparative plot to generate
        """
        if plot_type == "domain_comparison":
            self.family_visualizer.plot_domain_comparison(families)
        elif plot_type == "architecture_comparison":
            self.family_visualizer.plot_architecture_comparison(families)
        else:
            raise ValueError(f"Unknown comparative plot type: {plot_type}")
    
    def export_plot_data(self, family: Family, plot_type: str, output_path: str) -> None:
        """
        Export plot data to a file.
        
        Args:
            family: Family object
            plot_type: Type of plot data to export
            output_path: Path to save the data
        """
        if plot_type == "domain_data":
            data = self._extract_domain_data(family)
        elif plot_type == "statistics":
            data = self._extract_statistics_data(family)
        else:
            raise ValueError(f"Unknown data export type: {plot_type}")
        
        # Export data (implementation depends on format)
        self._write_data_to_file(data, output_path)
    
    def _extract_domain_data(self, family: Family) -> dict:
        """Extract domain data for export."""
        data = {
            'family_id': family.family_id,
            'systems': []
        }
        
        for system in family.systems:
            system_data = {
                'system_id': system.sys_id,
                'length': system.sys_len,
                'domains': []
            }
            
            for domain in system.domains:
                domain_data = {
                    'id': domain.dom_id,
                    'start': domain.start,
                    'end': domain.end,
                    'type': domain.type,
                    'bitscore': domain.bitscore,
                    'coverage': domain.coverage
                }
                system_data['domains'].append(domain_data)
            
            data['systems'].append(system_data)
        
        return data
    
    def _extract_statistics_data(self, family: Family) -> dict:
        """Extract statistics data for export."""
        # Implementation would depend on what statistics are needed
        return {
            'family_id': family.family_id,
            'num_systems': len(family.systems),
            'total_domains': sum(len([d for d in s.domains if not d.is_hole]) for s in family.systems)
        }
    
    def _write_data_to_file(self, data: dict, output_path: str) -> None:
        """Write data to file (placeholder implementation)."""
        # Implementation would depend on desired output format (JSON, CSV, etc.)
        pass
    
    def get_available_plot_types(self) -> List[str]:
        """
        Get list of available plot types.
        
        Returns:
            List of available plot types
        """
        return [
            "general",
            "char", 
            "arch",
            "holes",
            "summary",
            "char_rescue"
        ]
    
    def get_plot_description(self, plot_type: str) -> str:
        """
        Get description of a plot type.
        
        Args:
            plot_type: Type of plot
            
        Returns:
            Description of the plot type
        """
        descriptions = {
            "general": "General domain distribution plots",
            "char": "Characteristic domain analysis plots",
            "arch": "Domain architecture visualizations",
            "holes": "Inter-domain region (hole) analysis",
            "summary": "Summary statistics plots",
            "char_rescue": "Rescue-specific characteristic plots"
        }
        
        return descriptions.get(plot_type, "Unknown plot type") 