import pytest
import pandas as pd
from datetime import datetime as dt
from unittest.mock import patch

from main import read_files_from_dir, parse_xml, parse_window_parameter, window_by_datetime, process_to_RO

"""
Static test cases for the functions in main.py using the library pytest.
Adding more tests for edge cases and invalid inputs would help with the robustness of the tests.
We could also paramterize the tests to reduce code redundancy and improve readability.
"""

@patch('main.Path.rglob')
@patch('builtins.open')
def test_read_files_from_dir(mock_open, mock_rglob):
    # Mock XML file read
    mock_rglob.return_value = ['file1.xml', 'file2.xml']
    mock_open.return_value.__enter__.return_value.read.side_effect = [
        "<event><order_id>101</order_id></event>",
        "<event><order_id>102</order_id></event>"
    ]
    result = read_files_from_dir('mock_dir')
    assert len(result) == 2

def test_parse_xml():
    # Mock XML string
    xml_string = '''
    <event>
        <order_id>103</order_id>
        <date_time>2023-08-10T16:00:00</date_time>
        <status>Completed</status>
        <cost>120.00</cost>
        <repair_details>
            <technician>Mary Johnson</technician>
            <repair_parts>
                <part name="Brake Pad" quantity="4"/>
                <part name="Air Filter" quantity="1"/>
            </repair_parts>
        </repair_details>
    </event>
    '''
    result = parse_xml([xml_string])
    assert len(result) == 1
    assert result.iloc[0]['order_id'] == '103'
    assert result.iloc[0]['status'] == 'Completed'
    assert result.iloc[0]['technician'] == 'Mary Johnson'
    assert isinstance(result.iloc[0]['repair_parts'], list)
    assert result.iloc[0]['repair_parts'][0]['name'] == 'Brake Pad'

def test_parse_window_parameter():
    # Test valid window parameters
    assert parse_window_parameter('5H') == (5, 'H')
    assert parse_window_parameter('3D') == (3, 'D')
    assert parse_window_parameter('1W') == (1, 'W')

    # Test invalid parameter
    with pytest.raises(ValueError):
        parse_window_parameter('2M')

def test_window_by_datetime():
    # Mock DataFrame
    data = pd.DataFrame({
        'order_id': ['103', '104'],
        'date_time': [
            dt.strptime("2023-08-10T16:00:00", "%Y-%m-%dT%H:%M:%S"),
            dt.strptime("2023-08-11T12:00:00", "%Y-%m-%dT%H:%M:%S")
        ],
        'status': ['Completed', 'Pending'],
        'cost': ['120.00', '150.00'],
        'technician': ['Mary Johnson', 'John Doe'],
        'repair_parts': [
            [{'name': 'Brake Pad', 'quantity': '4'}],
            [{'name': 'Oil Filter', 'quantity': '1'}]
        ]
    })

    result = window_by_datetime(data, '1D')
    assert len(result) == 1
    key = list(result.keys())[0]
    assert 'Latest 1D ending' in key
    assert len(result[key]) == 2
    assert result[key].iloc[0]['order_id'] == '103'
    assert result[key].iloc[1]['order_id'] == '104'

def test_process_to_RO():
    # Mock windowed data
    mock_data = {
        'window_1': pd.DataFrame({
            'order_id': ['103'],
            'date_time': [dt.strptime("2023-08-10T16:00:00", "%Y-%m-%dT%H:%M:%S")],
            'status': ['Completed'],
            'cost': ['120.00'],
            'technician': ['Mary Johnson'],
            'repair_parts': [[{'name': 'Brake Pad', 'quantity': '4'}]]
        })
    }
    result = process_to_RO(mock_data)
    assert len(result) == 1
    assert result[0].order_id == '103'
    assert result[0].technician == 'Mary Johnson'
    assert isinstance(result[0].repair_parts, str)

if __name__ == '__main__':
    pytest.main()