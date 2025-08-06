"""
Unit tests for the argument parser.
"""

import pytest
import os
from unittest.mock import patch, mock_open
from src.cli.argument_parser import parse_arguments, ArgumentError, create_processing_config


class TestArgumentParser:
    """Test cases for the argument parser."""
    
    def test_parse_arguments_cdd_input(self):
        """Test parsing arguments with CDD input."""
        with patch('sys.argv', ['script', '-c', 'test.cdd', '-p', 'general', '-o', '/tmp/output']), \
             patch('os.path.isfile', return_value=True):
            args, is_file = parse_arguments()
            
            assert args.cdd_input == 'test.cdd'
            assert args.rescue_input is None
            assert args.plot == 'general'
            assert args.output == '/tmp/output'
            assert args.merge_overlapping_domains == 1
            assert is_file == ''
    
    def test_parse_arguments_rescue_input(self):
        """Test parsing arguments with rescue input."""
        with patch('sys.argv', ['script', '-r', 'rescue_dir', '-p', 'char_rescue']), \
             patch('os.path.isdir', return_value=True):
            args, is_file = parse_arguments()
            
            assert args.rescue_input == 'rescue_dir'
            assert args.cdd_input is None
            assert args.plot == 'char_rescue'
            assert args.output == 'output/'
            assert is_file == ''
    
    def test_parse_arguments_with_tcids_file(self):
        """Test parsing arguments with TCIDs from file."""
        with patch('sys.argv', ['script', '-c', 'test.cdd', '-t', 'tcids.txt']), \
             patch('os.path.isfile', return_value=True), \
             patch('builtins.open', mock_open(read_data='1.A.1\n2.A.1\n')):
            args, is_file = parse_arguments()
            
            assert args.tcids == 'tcids.txt'
            assert is_file is True
    
    def test_parse_arguments_with_tcids_list(self):
        """Test parsing arguments with TCIDs as comma-separated list."""
        with patch('sys.argv', ['script', '-c', 'test.cdd', '-t', '1.A.1,2.A.1']), \
             patch('os.path.isfile', side_effect=lambda x: x == 'test.cdd'):
            args, is_file = parse_arguments()
            
            assert args.tcids == '1.A.1,2.A.1'
            assert is_file is False
    
    def test_parse_arguments_merge_option(self):
        """Test parsing merge overlapping domains option."""
        with patch('sys.argv', ['script', '-c', 'test.cdd', '-m', '0']), \
             patch('os.path.isfile', return_value=True):
            args, is_file = parse_arguments()
            
            assert args.merge_overlapping_domains == 0
    
    def test_parse_arguments_mutually_exclusive_inputs(self):
        """Test that CDD and rescue inputs are mutually exclusive."""
        with patch('sys.argv', ['script', '-c', 'test.cdd', '-r', 'rescue_dir']):
            with pytest.raises(SystemExit):
                parse_arguments()
    
    def test_parse_arguments_missing_input(self):
        """Test that input is required."""
        with patch('sys.argv', ['script', '-p', 'general']):
            with pytest.raises(SystemExit):
                parse_arguments()
    
    def test_create_processing_config(self):
        """Test creating processing configuration from arguments."""
        with patch('sys.argv', ['script', '-c', 'test.cdd', '-p', 'general,char', '-o', '/tmp/output', '-m', '1']), \
             patch('os.path.isfile', return_value=True):
            args, is_file = parse_arguments()
            config = create_processing_config(args)
            
            assert config['merge_overlapping_domains'] is True
            assert config['plot_types'] == ['general', 'char']
            assert config['output_directory'] == '/tmp/output'
            assert config['input_type'] == 'cdd'
            assert config['input_path'] == 'test.cdd'
    
    def test_create_processing_config_rescue(self):
        """Test creating processing configuration for rescue input."""
        with patch('sys.argv', ['script', '-r', 'rescue_dir', '-p', 'char_rescue']), \
             patch('os.path.isdir', return_value=True):
            args, is_file = parse_arguments()
            config = create_processing_config(args)
            
            assert config['input_type'] == 'rescue'
            assert config['input_path'] == 'rescue_dir'
            assert config['plot_types'] == ['char_rescue']
    
    def test_create_processing_config_no_plots(self):
        """Test creating processing configuration without plots."""
        with patch('sys.argv', ['script', '-c', 'test.cdd']), \
             patch('os.path.isfile', return_value=True):
            args, is_file = parse_arguments()
            config = create_processing_config(args)
            
            assert config['plot_types'] == []
    
    def test_create_processing_config_with_data_file(self):
        """Test creating processing configuration with data file."""
        with patch('sys.argv', ['script', '-c', 'test.cdd', '-d', 'output.csv']), \
             patch('os.path.isfile', return_value=True):
            args, is_file = parse_arguments()
            config = create_processing_config(args)
            
            assert config['data_file'] == 'output.csv'
    
    def test_create_processing_config_with_family_ids(self):
        """Test creating processing configuration with family IDs."""
        with patch('sys.argv', ['script', '-c', 'test.cdd', '-t', '1.A.1,2.A.1']), \
             patch('os.path.isfile', side_effect=lambda x: x == 'test.cdd'):
            args, is_file = parse_arguments()
            config = create_processing_config(args)
            
            assert config['family_ids'] == '1.A.1,2.A.1'
    
    def test_validate_arguments_valid_cdd_file(self):
        """Test validation with valid CDD file."""
        with patch('sys.argv', ['script', '-c', 'test.cdd']), \
             patch('os.path.isfile', return_value=True):
            args, is_file = parse_arguments()
            # Should not raise any exceptions
    
    def test_validate_arguments_invalid_cdd_file(self):
        """Test validation with invalid CDD file."""
        with patch('sys.argv', ['script', '-c', 'nonexistent.cdd']), \
             patch('os.path.isfile', return_value=False):
            with pytest.raises(ArgumentError, match="CDD input file not found"):
                parse_arguments()
    
    def test_validate_arguments_invalid_rescue_dir(self):
        """Test validation with invalid rescue directory."""
        with patch('sys.argv', ['script', '-r', 'nonexistent_dir']), \
             patch('os.path.isdir', return_value=False):
            with pytest.raises(ArgumentError, match="Rescue input directory not found"):
                parse_arguments()
    
    def test_validate_arguments_invalid_plot_type(self):
        """Test validation with invalid plot type."""
        with patch('sys.argv', ['script', '-c', 'test.cdd', '-p', 'invalid_plot']), \
             patch('os.path.isfile', return_value=True):
            with pytest.raises(ArgumentError, match="Invalid plot types"):
                parse_arguments()
    
    def test_validate_arguments_invalid_tcids(self):
        """Test validation with invalid TCIDs."""
        with patch('sys.argv', ['script', '-c', 'test.cdd', '-t', 'invalid_tcid']), \
             patch('os.path.isfile', side_effect=lambda x: x == 'test.cdd'):
            with pytest.raises(ArgumentError, match="Invalid family IDs"):
                parse_arguments()
    
    def test_validate_arguments_invalid_merge_option(self):
        """Test validation with invalid merge option."""
        with patch('sys.argv', ['script', '-c', 'test.cdd', '-m', '2']), \
             patch('os.path.isfile', return_value=True):
            with pytest.raises(SystemExit):  # argparse will exit for invalid choice
                parse_arguments()
    
    def test_validate_arguments_output_directory(self):
        """Test validation of output directory."""
        with patch('sys.argv', ['script', '-c', 'test.cdd', '-o', '/tmp/test_output']), \
             patch('os.path.isfile', return_value=True), \
             patch('os.makedirs') as mock_makedirs:
            args, is_file = parse_arguments()
            # Should not raise any exceptions
            # The actual directory creation would happen during processing 