"""
Family visualizer for TCDB Domain Visualization.

This module provides visualization functionality for family-level plots.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import List
from ..core.family import Family
from ..utils.file_utils import combine_svgs


class FamilyVisualizer:
    """
    Visualizer for family-level plots and charts.
    """
    
    def __init__(self):
        """Initialize the family visualizer."""
        # Set up plotting style
        plt.style.use('default')
        sns.set_palette("husl")
    
    def plot_domain_architecture(self, family: Family) -> None:
        """
        Generate domain architecture plots for each system.
        
        Args:
            family: Family object to visualize
        """
        svgs = []
        max_sys_len = max(system.sys_len for system in family.systems)
        
        for system in family.systems:
            # Count non-hole domains for sizing
            non_hole_domains = [dom for dom in system.domains if not dom.is_hole]
            size = max(1, len(non_hole_domains))
            
            fig, ax = plt.subplots(figsize=(16, 0.25 * (size + 2)))
            
            ax.set_title(system.sys_id)
            ax.set_xlabel('Residue Position')
            ax.set_ylabel('Domains')
            
            # Plot protein backbone
            space = np.linspace(0, system.sys_len - 1, 2)
            cnt = 0
            dom_ids = [system.sys_id.split('-')[0] if '-' in system.sys_id else system.sys_id]
            ax.plot(space, [cnt] * 2, 'k-', linewidth=2)
            
            # Plot domains
            for domain in system.domains:
                if domain.is_hole:
                    continue
                cnt -= 1
                dom_ids.append(domain.dom_id)
                space = np.linspace(domain.start, domain.end, 2)
                
                # Color based on whether it's characteristic
                if domain.dom_id in family.characteristic_domains:
                    color = 'red'
                else:
                    color = 'blue'
                
                ax.plot(space, [cnt] * 2, color=color, label=domain.dom_id, linewidth=8)
            
            # Set consistent axis limits
            ax.set_xlim(0, max_sys_len)
            ax.set_ylim(cnt - 1, 1)
            ax.set_yticks(range(0, cnt - 1, -1))
            ax.set_yticklabels(dom_ids)
            
            # Save as SVG
            svg_file = str(family.output_directory / f"general-{system.sys_id}.svg")
            fig.savefig(svg_file, format='svg', bbox_inches='tight', pad_inches=0.2)
            svgs.append(svg_file)
            plt.close(fig)
        
        # Combine SVGs into HTML
        combine_svgs(svgs, f"general-{family.family_id}.html", str(family.output_directory), "general")
    
    def plot_characteristic_domains(self, family: Family) -> None:
        """
        Generate plots showing only characteristic domains for each system.
        
        Args:
            family: Family object to visualize
        """
        if not family.characteristic_domains:
            return
            
        svgs = []
        max_sys_len = max(system.sys_len for system in family.systems)
        
        for system in family.systems:
            char_domains = [dom for dom in system.domains if not dom.is_hole and dom.dom_id in family.characteristic_domains]
            
            if not char_domains:
                continue
                
            fig, ax = plt.subplots(figsize=(16, 0.3 * (len(char_domains) + 2)))
            
            ax.set_title(system.sys_id)
            ax.set_xlabel('Residue Position')
            ax.set_ylabel('Domains')
            
            # Plot protein backbone
            space = np.linspace(0, system.sys_len - 1, 2)
            cnt = 0
            dom_ids = [system.sys_id.split('-')[0] if '-' in system.sys_id else system.sys_id]
            ax.plot(space, [cnt] * 2, 'k-', linewidth=2)
            
            # Plot characteristic domains
            for domain in char_domains:
                cnt -= 1
                dom_ids.append(domain.dom_id)
                space = np.linspace(domain.start, domain.end, 2)
                ax.plot(space, [cnt] * 2, color='red', label=domain.dom_id, linewidth=8)
            
            # Set consistent axis limits
            ax.set_xlim(0, max_sys_len)
            ax.set_ylim(cnt - 1, 1)
            ax.set_yticks(range(0, cnt - 1, -1))
            ax.set_yticklabels(dom_ids)
            
            # Save as SVG
            svg_file = str(family.output_directory / f"char-{system.sys_id}.svg")
            fig.savefig(svg_file, format='svg', bbox_inches='tight', pad_inches=0.2)
            svgs.append(svg_file)
            plt.close(fig)
        
        # Combine SVGs into HTML
        if svgs:
            combine_svgs(svgs, f"char-{family.family_id}.html", str(family.output_directory), "char")
    
    def plot_holes(self, family: Family) -> None:
        """
        Generate visualization of inter-domain regions (holes) across systems.
        
        Args:
            family: Family object to visualize
        """
        fig, ax = plt.subplots(figsize=(16, 0.3 * (len(family.systems) + 2)))
        
        # Set y-ticks and y-tick labels
        ax.set_yticks(range(len(family.systems)))
        sys_ids = [sys.sys_id.split('-')[0] if '-' in sys.sys_id else sys.sys_id for sys in family.systems]
        ax.set_yticklabels(sys_ids)
        
        # Plot protein backbones
        for i, system in enumerate(family.systems):
            ax.barh(i, system.sys_len, left=0, color="red", height=0.03)
        
        # Plot holes
        hole_colors = plt.cm.tab10(range(len(family.systems)))
        for i, system in enumerate(family.systems):
            for hole in system.holes:
                ax.barh(i, hole.end - hole.start, color=hole_colors[i], 
                       left=hole.start, height=0.4)
        
        ax.set_xlabel('Residue Position')
        ax.set_title(f'{family.family_id} Holes')
        
        # Save as SVG
        svg_file = str(family.output_directory / f"holes-{family.family_id}.svg")
        fig.savefig(svg_file, format='svg', bbox_inches='tight')
        plt.close(fig)
        
        # Combine into HTML
        combine_svgs([svg_file], f"holes-{family.family_id}.html", str(family.output_directory), "holes")
    
    def plot_summary_statistics(self, family: Family) -> None:
        """
        Generate a summary plot showing domain coverage across all systems.
        
        Args:
            family: Family object to visualize
        """
        fig, ax = plt.subplots(figsize=(16, 0.3 * (len(family.systems) + 2)))
        
        for i, system in enumerate(family.systems):
            # Plot domains
            for domain in system.domains:
                if not domain.is_hole:
                    ax.barh(i, domain.end - domain.start, left=domain.start, 
                           height=0.4, color='blue')
            
            # Plot holes
            for hole in system.holes:
                ax.barh(i, hole.end - hole.start, left=hole.start, 
                       height=0.03, color='red')
        
        # Set y-ticks and y-tick labels
        ax.set_yticks(range(len(family.systems)))
        sys_ids = [sys.sys_id.split('-')[0] if '-' in sys.sys_id else sys.sys_id for sys in family.systems]
        ax.set_yticklabels(sys_ids)
        
        ax.set_xlabel('Residue Position')
        ax.set_title(f'{family.family_id} Summary')
        
        # Save as SVG
        svg_file = str(family.output_directory / f"summary-{family.family_id}.svg")
        fig.savefig(svg_file, format='svg', bbox_inches='tight')
        plt.close(fig)
        
        # Combine into HTML
        combine_svgs([svg_file], f"summary-{family.family_id}.html", str(family.output_directory), "summary")
    
    def plot_architecture(self, family: Family) -> None:
        """
        Generate a consensus architecture plot for the family.
        
        Args:
            family: Family object to visualize
        """
        if len(family.systems) <= 2:
            print("System count too small, unable to accurately construct architecture. Skipping arch plot...")
            return
        
        char_domain_locs = {k: [] for k in family.characteristic_domains}
        char_domain_map = {}
        
        # Store char domain locations
        for system in family.systems:
            sys_dom_locs = {k: [] for k in family.characteristic_domains}
            for domain in system.domains:
                if domain.dom_id in char_domain_locs:
                    sys_dom_locs[domain.dom_id].append([domain.start / system.sys_len, domain.end / system.sys_len])
            
            for char_dom in family.characteristic_domains:
                char_domain_locs[char_dom].append(sys_dom_locs[char_dom])
        
        # Analyze structure, choose majority appearances (mode)
        for char_dom in family.characteristic_domains:
            curr_lst = char_domain_locs[char_dom]
            
            # Get mode of domain counts
            from scipy import stats
            curr_mode = stats.mode([len(lst) for lst in curr_lst if len(lst) > 0])
            curr_lst = [lst for lst in curr_lst if len(lst) == curr_mode.mode]
            
            if curr_mode.mode > 1:
                for i in range(curr_mode.mode):
                    char_domain_locs[char_dom + ' ' + str(i)] = [lst[i] for lst in curr_lst]
                del char_domain_locs[char_dom]
            else:
                char_domain_locs[char_dom] = [lst[0] for lst in curr_lst]

        # Calculate confidence intervals
        from ..utils.file_utils import confidence_interval_mean
        for char_dom, intervals in char_domain_locs.items():
            start = confidence_interval_mean([i[0] for i in intervals])
            end = confidence_interval_mean([i[1] for i in intervals])
            
            components = char_dom.split(' ')
            if len(components) > 1:
                if components[0] in char_domain_map:
                    char_domain_map[components[0]].append([start * 100, end * 100])
                else:
                    char_domain_map[components[0]] = [[start * 100, end * 100]]
            else:
                char_domain_map[char_dom] = [[start * 100, end * 100]]
        
        # Create plot
        cnt = 0
        fig, ax = plt.subplots(figsize=(16, 0.25 * (len(family.characteristic_domains) + 15)))
        
        for char_dom, intervals in char_domain_map.items():
            for interval in intervals:
                space = np.linspace(interval[0], interval[1], 2)
                ax.plot(space, [cnt] * 2, color='red', label=char_dom.split(' ')[0], linewidth=8)
            cnt += 1
        
        ax.set_yticks(range(len(char_domain_map)))
        ax.set_yticklabels(list(char_domain_map.keys()))
        
        ax.set_xlabel('Residue Percentile %')
        ax.set_title(f'{family.family_id} Architecture')
        ax.set_xlim(-1, 101)
        
        # Save as SVG
        svg_file = str(family.output_directory / f"arch-{family.family_id}.svg")
        fig.savefig(svg_file, format='svg', bbox_inches='tight')
        plt.close(fig)
        
        # Combine into HTML
        combine_svgs([svg_file], f"arch-{family.family_id}.html", str(family.output_directory), "arch") 