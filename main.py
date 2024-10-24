import os
import logging
import time
from typing import Dict, List
from pathlib import Path

import pandas as pd
import xml.etree.ElementTree as ET

# Logging Setup
logs_directory = 'logs'
os.makedirs(logs_directory, exist_ok=True)
log_filename = time.strftime("%Y%m%d-%H%M%S_pipeline_logs.txt")
log_filepath = os.path.join(logs_directory, log_filename)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=log_filepath,
)

def read_files_from_dir(dir: str) -> List[str]:
    """
    Read xml files from a directory and returns a list of XML contents.
    """
    logger = logging.getLogger("read_files_from_dir")

    xml_data = []
    xml_files = Path(dir).rglob('*.xml')

    for file in xml_files:
        try:
            with open(file, 'r') as f:
                xml_data.append(f.read())
            logging.info(f"File read successfully: {file}")

        except Exception as e:
            logger.error(f"Error reading file: {file}; {e}")

    return xml_data


def parse_xml(files: List[str]) -> Dict:
    """
    Parse XML contents and returns a dictionary of parsed data.
    """
    parsed_data = {}
    for file in files:
        root = ET.fromstring(file)
        for child in root:
            parsed_data[child.tag] = child.text

    return parsed_data