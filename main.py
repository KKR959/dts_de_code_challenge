import os
import logging
import time
import sqlite3
import pandas as pd
import xml.etree.ElementTree as ET

from typing import Dict, List
from pathlib import Path
from datetime import datetime as dt

from utils.main_sql import CREATE_TABLE_REPAIR_ORDER, INSERT_REPAIR_ORDER
from utils.ro import RO
from utils.helpers import parse_window_parameter

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
    Read xml files from a directory and returns a list of strings containing the XML contents.
    """
    logger = logging.getLogger("read_files_from_dir")

    xml_contents = []
    xml_files = Path(dir).rglob('*.xml')

    for file in xml_files:
        try:
            with open(file, 'r') as f:
                xml_contents.append(f.read())
            logger.info(f"File read successfully: {file}")

        except Exception as e:
            logger.error(f"Error reading file: {file}; {e}")

    return xml_contents


def parse_xml(files: List[str]) -> pd.DataFrame:
    """
    Parse XML contents into a Pandas Dataframe.
    """
    logger = logging.getLogger("parse_xml")

    parsed_data = []

    for file in files:
        try:
            element = ET.fromstring(file)

            order_id = element.find('order_id').text
            date_time = element.find('date_time').text
            status = element.find('status').text
            cost = element.find('cost').text
            technician = element.find('./repair_details/technician').text

            parts = element.findall('./repair_details/repair_parts/part')
            repair_parts = [{
                'name': part.get('name'),
                'quantity': part.get('quantity')
            } for part in parts]

            parsed_data.append({
                'order_id': order_id,
                'date_time': dt.strptime(date_time, "%Y-%m-%dT%H:%M:%S"),
                'status': status,
                'cost': cost,
                'technician': technician,
                'repair_parts': repair_parts
            })

            logger.info(f"XML Parse Successful; order_id {order_id}")

        except ET.ParseError as e:
            logger.error(f"Malformed XML structure, skipping file: {e}")
        except Exception as e:
            logger.error(f"Error parsing XML Content: {e}")

    return pd.DataFrame(parsed_data)


def window_by_datetime(data: pd.DataFrame, window: str) -> Dict[str, pd.DataFrame]:
    """
    Filters the data by the specified window based on the date_time column and returns the latest event for each unique order_id.
    The function returns a dictionary where keys are window identifiers and values are DataFrames for each window.
    """
    logger = logging.getLogger("window_by_datetime")
    windowed_data = {}

    try:
        # Parse the window parameter passed by the user
        number, unit = parse_window_parameter(window)
        freq = f'{number}{unit}'

        # calculate the cutoff date for filtering based on the window parameter
        most_recent_date = data['date_time'].max()
        cutoff_date = most_recent_date - pd.to_timedelta(number, unit=unit)

        # Filter the data to include only entries within the specified window
        filtered_data = data[data['date_time'] >= cutoff_date]
        
        if filtered_data.empty:
            logger.warning("No data found within the specified window.")
            return windowed_data
        
        # Group by order_id to get the latest event for each unique repair order in the filtered window
        latest_events = filtered_data.sort_values(by='date_time').groupby('order_id').last().reset_index()

        # Create a window key using a formatted string based on the most recent data
        window_key = f"Latest {number}{unit} ending {most_recent_date.strftime('%Y-%m-%d %H:%M:%S')}"
        windowed_data[window_key] = latest_events

        logger.info(f"Data filtered by {window} successfully.")
    except ValueError as e:
        logger.error(f"Error filtering data by {window}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error filtering data by {window}: {e}")
        return {}

    return windowed_data


def process_to_RO(data: Dict[str, pd.DataFrame]) -> List[RO]:
    """
    Transforms the windowed data into a list of structured RO objects
    """
    logger = logging.getLogger("process_to_RO")
    
    ro_list = []
    try:
        # Iterate over each window and create a RO object for each entry
        for window, df in data.items():
            for index, row in df.iterrows():
                ro = RO(
                    order_id=row['order_id'],
                    date_time=row['date_time'],
                    status=row['status'],
                    cost=row['cost'],
                    technician=row['technician'],
                    repair_parts=row['repair_parts']
                )

                ro_list.append(ro)

        if not ro_list:
            logger.warning("No data to process into RO objects.")
        else:
            logger.info(f"Successfully processed data into {len(ro_list)} RO objects.")
    except Exception as e:
        logger.error(f"Error processing data into RO objects: {e}")
    return ro_list


def write_to_sqlite(ro_list: List[RO], db_name: str = 'repair_orders.db'):
    """
    Writes the RO objects to a SQLite database

    Current behavior is to overwrite records where an order_id already exists evertime the script is called.
    Depending on how we wanted to keep track of the data, we could modify this behavior to only insert new records removing the unique constraint on order_id.
    If this route were to be taken processed_at field could be used to grab most recent updates of orders.
    """
    logger = logging.getLogger("write_to_sqlite")
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute(CREATE_TABLE_REPAIR_ORDER)

        for ro in ro_list:
            try:
                cursor.execute(INSERT_REPAIR_ORDER, ro.to_tuple())

                logger.info(f"Successfully wrote order_id: {ro.order_id} to database.")
            except Exception as e:
                logger.error(f"Error writing order_id: {ro.order_id} to database: {e}")
            
        conn.commit()
    except Exception as e:
        logger.error(f"Error connecting to or setting up database: {e}")
    finally:
        conn.close()


def pipeline(dir: str, window: str):
    logger = logging.getLogger("pipeline")
    try:
        xml_files = read_files_from_dir(dir)
        parsed_data = parse_xml(xml_files)
        
        if parsed_data.empty:
            logger.warning("No valid data parsed from XML files, ending pipeline.")
            return
        
        windowed_data = window_by_datetime(parsed_data, window)
        if not windowed_data:
            logger.warning("No data available after windowing, ending pipeline.")
            return
        
        ro_list = process_to_RO(windowed_data)
        
        if not ro_list:
            logger.warning("No data to write to SQLite, ending pipeline.")
            return
        
        write_to_sqlite(ro_list)
        logger.info("Done")
    except Exception as e:
        logger.error(f"Error running pipeline: {e}")

if __name__ == '__main__':
    pipeline('data', window='1H')