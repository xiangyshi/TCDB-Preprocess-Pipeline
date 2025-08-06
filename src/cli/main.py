"""
Main CLI entry point for TCDB Domain Visualization.

This module provides the main command-line interface for the TCDB Domain
Visualization tool.
"""

import sys
import time
import logging
from typing import List, Optional
from .argument_parser import parse_arguments, ArgumentError, create_processing_config
from ..services.family_service import FamilyService
from ..services.domain_service import DomainService
from ..services.visualization_service import VisualizationService
from ..utils.config import config
from ..utils.file_utils import write_csv_data
import os


def setup_logging(level: str = "INFO") -> None:
    """
    Set up logging configuration.
    
    Args:
        level: Logging level
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('tcdb_visualization.log')
        ]
    )


def process_families(
    config_dict: dict,
    family_service: FamilyService,
    domain_service: DomainService,
    visualization_service: VisualizationService
) -> List[List[str]]:
    """
    Process families and generate outputs.
    
    Args:
        config_dict: Processing configuration
        family_service: Family processing service
        domain_service: Domain analysis service
        visualization_service: Visualization service
        
    Returns:
        List of CSV rows for data export
    """
    logger = logging.getLogger(__name__)
    
    # Get family data
    family_data = family_service.load_family_data(
        config_dict['input_path'],
        config_dict['input_type'],
        config_dict['family_ids']
    )
    
    if family_data.empty:
        logger.warning("No family data found")
        return []
    
    # Get unique family IDs
    unique_family_ids = family_data['family'].unique()
    logger.info(f"Processing {len(unique_family_ids)} families")
    
    # Process each family
    csv_rows = []
    start_time = time.time()
    
    for i, family_id in enumerate(unique_family_ids):
        logger.info(f"Processing family {family_id} ({i+1}/{len(unique_family_ids)})")
        
        try:
            # Get family data
            family_df = family_data[family_data['family'] == family_id]
            
            # Create family object
            family = family_service.create_family(
                family_df, 
                family_id, 
                config_dict['output_directory'],
                config_dict['merge_overlapping_domains'],
                config_dict['input_type']
            )
            
            # Generate plots if requested
            if config_dict['plot_types']:
                if "all" in config_dict['plot_types']:
                    visualization_service.generate_all_plots(family)
                else:
                    visualization_service.generate_plots(family, config_dict['plot_types'])
            
            # Generate CSV data if requested
            if config_dict['data_file']:
                family_csv_rows = family_service.generate_csv_data(family)
                csv_rows.extend(family_csv_rows)
                
        except Exception as e:
            logger.error(f"Error processing family {family_id}: {e}")
            continue
    
    # Log processing time
    end_time = time.time()
    processing_time = end_time - start_time
    minutes = int(processing_time // 60)
    seconds = int(processing_time % 60)
    logger.info(f"Processing completed in {minutes} minutes {seconds} seconds")
    
    return csv_rows


def main() -> int:
    """
    Main entry point for the CLI.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Parse arguments first
        args, is_file = parse_arguments()
        
        # Set up logging with the log level from arguments
        setup_logging(args.log_level)
        logger = logging.getLogger(__name__)
        
        config_dict = create_processing_config(args)
        
        # Ensure output directories exist
        config.ensure_directories()
        
        # Initialize services
        family_service = FamilyService()
        domain_service = DomainService()
        visualization_service = VisualizationService()
        
        # Process families
        csv_rows = process_families(
            config_dict,
            family_service,
            domain_service,
            visualization_service
        )
        
        # Write CSV data if requested
        if config_dict['data_file'] and csv_rows:
            csv_path = os.path.join(config_dict['output_directory'], config_dict['data_file'])
            headers = ["Accession", "Length", "Family", "Subfamily", "Domains", "Separators"]
            write_csv_data(csv_rows, csv_path, headers)
            logger.info(f"Data exported to {csv_path}")
        
        logger.info("Processing completed successfully")
        return 0
        
    except ArgumentError as e:
        logger.error(f"Argument error: {e}")
        return 1
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main()) 