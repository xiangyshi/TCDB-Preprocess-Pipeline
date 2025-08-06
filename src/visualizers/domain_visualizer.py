"""
Domain visualizer for TCDB Domain Visualization.

This module provides visualization functionality for domain-specific plots.
"""

import matplotlib.pyplot as plt
import seaborn as sns
from typing import List
from ..core.family import Family
from ..utils.file_utils import combine_svgs


class DomainVisualizer:
    """
    Visualizer for domain-specific plots and charts.
    """
    
    def __init__(self):
        """Initialize the domain visualizer."""
        # Set up plotting style
        plt.style.use('default')
        sns.set_palette("husl")
    
    def plot_general_domains(self, family: Family) -> None:
        """
        Generate general domain distribution plots.
        
        Args:
            family: Family object to visualize
        """
        # Create general domain distribution plot
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Collect domain data
        domain_data = []
        for system in family.systems:
            for domain in system.domains:
                if not domain.is_hole:
                    # Ensure numeric values
                    start = int(domain.start)
                    end = int(domain.end)
                    length = int(domain.length)
                    bitscore = float(domain.bitscore)
                    domain_data.append({
                        'system_id': system.sys_id,
                        'domain_id': domain.dom_id,
                        'start': start,
                        'end': end,
                        'length': length,
                        'bitscore': bitscore
                    })
        
        if not domain_data:
            return
        
        # Create scatter plot of domain positions
        starts = [d['start'] for d in domain_data]
        lengths = [d['length'] for d in domain_data]
        domain_ids = [d['domain_id'] for d in domain_data]
        
        # Color by domain type
        unique_domains = list(set(domain_ids))
        colors = plt.cm.tab10(range(len(unique_domains)))
        color_map = {dom: colors[i] for i, dom in enumerate(unique_domains)}
        
        for domain_id in unique_domains:
            mask = [d['domain_id'] == domain_id for d in domain_data]
            domain_starts = [starts[i] for i, m in enumerate(mask) if m]
            domain_lengths = [lengths[i] for i, m in enumerate(mask) if m]
            
            ax.scatter(domain_starts, domain_lengths, 
                      c=[color_map[domain_id]], label=domain_id, alpha=0.7)
        
        ax.set_xlabel('Domain Start Position')
        ax.set_ylabel('Domain Length')
        ax.set_title(f'Domain Distribution - Family {family.family_id}')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save plot as SVG
        svg_file = str(family.output_directory / f"domain_distribution-{family.family_id}.svg")
        plt.savefig(svg_file, format='svg', bbox_inches='tight')
        plt.close()
        
        # Combine into HTML
        combine_svgs([svg_file], f"domain_distribution-{family.family_id}.html", str(family.output_directory), "general")
    
    def plot_characteristic_domains(self, family: Family) -> None:
        """
        Generate characteristic domain analysis plots.
        
        Args:
            family: Family object to visualize
        """
        if not family.characteristic_domains:
            return
        
        # Create characteristic domain analysis plot
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # Plot 1: Characteristic domain frequency
        char_domains = family.characteristic_domains
        char_freq = [family.statistics['domain_frequencies'].get(d, 0) for d in char_domains]
        
        ax1.bar(range(len(char_domains)), char_freq, color='red', alpha=0.7)
        ax1.set_xticks(range(len(char_domains)))
        ax1.set_xticklabels(char_domains, rotation=45, ha='right')
        ax1.set_ylabel('Frequency')
        ax1.set_title('Characteristic Domain Frequency')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Systems with characteristic domains
        systems_with_char = []
        for system in family.systems:
            has_char = any(d.dom_id in char_domains for d in system.domains if not d.is_hole)
            systems_with_char.append(1 if has_char else 0)
        
        ax2.bar(['With Char', 'Without Char'], 
                [sum(systems_with_char), len(systems_with_char) - sum(systems_with_char)],
                color=['green', 'lightgray'], alpha=0.7)
        ax2.set_ylabel('Number of Systems')
        ax2.set_title('Systems with Characteristic Domains')
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Characteristic domain positions
        char_positions = []
        for system in family.systems:
            for domain in system.domains:
                if domain.dom_id in char_domains:
                    # Ensure we have numeric values
                    start_pos = int(domain.start)
                    sys_length = int(system.sys_len)
                    relative_pos = start_pos / sys_length
                    char_positions.append({
                        'domain_id': domain.dom_id,
                        'start': start_pos,
                        'system_length': sys_length,
                        'relative_position': relative_pos
                    })
        
        if char_positions:
            relative_positions = [p['relative_position'] for p in char_positions]
            ax3.hist(relative_positions, bins=20, alpha=0.7, color='orange', edgecolor='black')
            ax3.set_xlabel('Relative Position in Protein')
            ax3.set_ylabel('Frequency')
            ax3.set_title('Characteristic Domain Positions')
            ax3.grid(True, alpha=0.3)
        
        # Plot 4: Characteristic domain lengths
        char_lengths = []
        for system in family.systems:
            for domain in system.domains:
                if domain.dom_id in char_domains:
                    char_lengths.append(domain.length)
        
        if char_lengths:
            ax4.hist(char_lengths, bins=15, alpha=0.7, color='purple', edgecolor='black')
            ax4.set_xlabel('Domain Length')
            ax4.set_ylabel('Frequency')
            ax4.set_title('Characteristic Domain Lengths')
            ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save plot as SVG
        svg_file = str(family.output_directory / f"characteristic-{family.family_id}.svg")
        plt.savefig(svg_file, format='svg', bbox_inches='tight')
        plt.close()
        
        # Combine into HTML
        combine_svgs([svg_file], f"characteristic-{family.family_id}.html", str(family.output_directory), "char")
    
    def plot_rescue_characteristics(self, family: Family) -> None:
        """
        Generate rescue-specific characteristic plots.
        
        Args:
            family: Family object to visualize
        """
        # Create rescue-specific characteristic plots
        # This would be similar to characteristic plots but with rescue-specific analysis
        # Implementation depends on rescue data format and requirements
        
        # For now, create a basic rescue analysis plot
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Analyze rescue data characteristics
        rescue_stats = {
            'total_systems': len(family.systems),
            'systems_with_domains': len([s for s in family.systems if any(not d.is_hole for d in s.domains)]),
            'total_domains': sum(len([d for d in s.domains if not d.is_hole]) for s in family.systems),
            'unique_domains': len(set(d.dom_id for s in family.systems for d in s.domains if not d.is_hole))
        }
        
        # Create bar plot of rescue statistics
        categories = list(rescue_stats.keys())
        values = list(rescue_stats.values())
        
        ax.bar(categories, values, color='lightblue', alpha=0.7)
        ax.set_ylabel('Count')
        ax.set_title(f'Rescue Analysis - Family {family.family_id}')
        ax.grid(True, alpha=0.3)
        
        # Rotate x-axis labels
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Save plot as SVG
        svg_file = str(family.output_directory / f"rescue-{family.family_id}.svg")
        plt.savefig(svg_file, format='svg', bbox_inches='tight')
        plt.close()
        
        # Combine into HTML
        combine_svgs([svg_file], f"rescue-{family.family_id}.html", str(family.output_directory), "char")
    
    def plot_domain_frequency(self, family: Family) -> None:
        """
        Plot domain frequency across systems in the family.
        
        Args:
            family: Family object to visualize
        """
        # Count domain occurrences
        domain_counts = {}
        for system in family.systems:
            for domain in system.domains:
                if not domain.is_hole:
                    domain_counts[domain.dom_id] = domain_counts.get(domain.dom_id, 0) + 1
        
        if not domain_counts:
            return
        
        # Create plot
        plt.figure(figsize=(12, 6))
        domains = list(domain_counts.keys())
        counts = list(domain_counts.values())
        
        plt.bar(domains, counts)
        plt.title(f'Domain Frequency in Family {family.family_id}')
        plt.xlabel('Domain ID')
        plt.ylabel('Frequency')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Save plot as SVG
        svg_file = str(family.output_directory / f"domain_frequency-{family.family_id}.svg")
        plt.savefig(svg_file, format='svg', bbox_inches='tight')
        plt.close()
        
        # Combine into HTML
        combine_svgs([svg_file], f"domain_frequency-{family.family_id}.html", str(family.output_directory), "summary")
    
    def plot_domain_coverage(self, family: Family) -> None:
        """
        Plot domain coverage across systems in the family.
        
        Args:
            family: Family object to visualize
        """
        # Calculate domain coverage for each system
        coverages = []
        system_ids = []
        
        for system in family.systems:
            total_coverage = sum(domain.coverage for domain in system.domains if not domain.is_hole)
            coverages.append(total_coverage)
            system_ids.append(system.sys_id)
        
        if not coverages:
            return
        
        # Create plot
        plt.figure(figsize=(12, 6))
        plt.bar(range(len(system_ids)), coverages)
        plt.title(f'Domain Coverage in Family {family.family_id}')
        plt.xlabel('System')
        plt.ylabel('Total Domain Coverage')
        plt.xticks(range(len(system_ids)), system_ids, rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Save plot as SVG
        svg_file = str(family.output_directory / f"domain_coverage-{family.family_id}.svg")
        plt.savefig(svg_file, format='svg', bbox_inches='tight')
        plt.close()
        
        # Combine into HTML
        combine_svgs([svg_file], f"domain_coverage-{family.family_id}.html", str(family.output_directory), "summary") 