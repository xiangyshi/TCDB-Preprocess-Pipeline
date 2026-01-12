"""
Rescue family for TCDB Domain Visualization.

This module provides a specialized Family class for processing rescue data.
"""

import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import os
from typing import List
from .family import Family
from ..utils.file_utils import is_overlap, score_domain, combine_svgs


class RescueFamily(Family):
    """
    Specialized Family class for processing rescue data with domain filtering.
    """
    
    def __init__(self, rescue_data, family_id: str, output_directory: str, merge_overlapping: bool = True):
        """
        Initialize RescueFamily.
        
        Args:
            rescue_data: DataFrame containing rescue data
            family_id: Family identifier
            output_directory: Output directory for results
            merge_overlapping: Whether to merge overlapping domains
        """
        # Store rescue data for later use
        self.rescue_data = rescue_data
        
        # Create systems from rescue data first
        from ..services.family_service import FamilyService
        family_service = FamilyService()
        
        # Load sequences for this family
        from ..utils.config import config
        from ..utils.file_utils import read_sequence_file
        sequence_file_path = config.get_sequence_file_path(family_id)
        sequence_map = read_sequence_file(sequence_file_path)
        
        # Create systems using the family service logic
        systems = family_service._get_systems(rescue_data, family_id, sequence_map, merge_overlapping)
        
        # Initialize parent class with the created systems
        from pathlib import Path
        super().__init__(
            family_id=family_id,
            systems=systems,
            output_directory=Path(output_directory),
            merge_overlapping=merge_overlapping
        )
        
        # Apply rescue-specific filtering
        self.filter_domains()
    
    def filter_domains(self):
        """
        Filter domains using graph-based approach to handle overlapping domains.
        """
        votes = {}
        
        for sys in self.systems:
            # Create a graph
            G = nx.Graph()

            sys_domains = [dom for dom in sys.domains if dom.type != "hole"]
            # Add nodes for each domain
            for dom in sys_domains:
                G.add_node(dom.dom_id, domain=dom)

            # Add edges for overlapping domains
            for i in range(len(sys_domains)):
                for j in range(i + 1, len(sys_domains)):
                    if is_overlap(sys_domains[i], sys_domains[j]):
                        G.add_edge(sys_domains[i].dom_id, sys_domains[j].dom_id)

            # Find connected components
            connected_components = list(nx.connected_components(G))

            # TODO: retain overlapping domain information
            sys.overlapping_domains = [G.nodes[i]['domain'] for component in connected_components for i in component]

            # Select representative domain for each connected component
            sys_new_domains = []
            for component in connected_components:
                # Select the domain with the highest score
                max_score = float('-inf')
                representative_domain = None
                for i in component:
                    
                    domain = G.nodes[i]['domain']
                    score = score_domain(domain, sys.sys_len)  # Calculate the score for the domain
                    if score > max_score:
                        max_score = score
                        representative_domain = domain
                
                # Store the representative domain for the component
                if representative_domain:
                    sys_new_domains.append(representative_domain)
                    if representative_domain.dom_id not in votes:
                        votes[representative_domain.dom_id] = 0
                    votes[representative_domain.dom_id] += 1
            sys.domains = sys_new_domains
        
        # Sort the votes
        sorted_votes = sorted(votes.items(), key=lambda x: x[1], reverse=True)
        scores = {key: 0 for key in votes.keys()}
        
        # Determine best domain for family
        for sys in self.systems:
            for dom in sys.overlapping_domains:
                for rep_dom, value in sorted_votes:
                    if dom.dom_id == rep_dom:
                        scores[dom.dom_id] += value * dom.coverage
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        # Replace domains with best domain
        for sys in self.systems:
            for i, dom in enumerate(sys.domains):
                for best_dom, score in sorted_scores:
                    if dom.dom_id == best_dom:
                        break
                    try:
                        curr_bests = sys.domain_map[best_dom]
                    except KeyError:
                        # If the best domain is not in the domain map, skip it
                        continue
                    # Check if the current domain is overlapping with any of the best domains
                    for curr_best in curr_bests:
                        if is_overlap(dom, curr_best):
                            sys.domains[i] = curr_best
                            break
        for sys in self.systems:
            sys.fill_holes()
            sys.get_holes()
    
    def plot_characteristic_rescue(self, label: str = ""):
        """
        Generate characteristic domain plots with rescue information.
        
        Args:
            label: Optional label for the plot
        """
        svgs = []
        colors = ["green", "orange", "red"]
        
        for i, system in enumerate(self.systems):
            sys_doms = [dom for dom in system.domains if dom.type != "hole"]
            fig, ax = plt.subplots(figsize=(16, 0.3 * (len(sys_doms) + 2)))
            
            ax.set_title(system.sys_id)
            ax.set_xlabel('Residue Position')
            ax.set_ylabel('Domains')

            # Plot protein backbone
            space = np.linspace(0, system.sys_len - 1, 2)
            cnt = 0
            dom_ids = [system.sys_id.split('-')[0] if '-' in system.sys_id else system.sys_id]
            ax.plot(space, [cnt] * 2, 'k-', linewidth=2)
            
            for domain in sys_doms:
                cnt -= 1
                dom_ids.append(domain.dom_id)
                
                # Get rescue round information from the data
                rescue_round = getattr(domain, 'rescue_round', 0)
                if rescue_round is None:
                    rescue_round = 0
                color = colors[min(rescue_round, len(colors) - 1)]
                
                space = np.linspace(domain.start, domain.end, 2)
                ax.plot(space, [cnt] * 2, color=color, label=domain.dom_id, linewidth=8)

            # Set consistent axis limits
            max_sys_len = max(system.sys_len for system in self.systems) if self.systems else 1000
            ax.set_xlim(0, max_sys_len)
            ax.set_ylim(cnt - 1, 1)
            ax.set_yticks(range(0, cnt - 1, -1))
            ax.set_yticklabels(dom_ids)

            # Save as SVG
            if isinstance(self.output_directory, str):
                output_dir = self.output_directory
            else:
                output_dir = str(self.output_directory)
            
            svg_file = os.path.join(output_dir, f"rescue-{system.sys_id}.svg")
            fig.savefig(svg_file, format='svg', bbox_inches='tight', pad_inches=0.2)
            svgs.append(svg_file)
            plt.close(fig)
        
        # Combine SVGs into HTML
        combine_svgs(svgs, f"rescue-{self.family_id}.html", output_dir, "rescue")
    
    def plot(self, options: List[str] = None):
        """
        Generate plots for the rescue family.
        
        Args:
            options: List of plot types to generate
        """
        if options is None:
            options = ["char_rescue"]
        
        if "char_rescue" in options:
            self.plot_characteristic_rescue() 