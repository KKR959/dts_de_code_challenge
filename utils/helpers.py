import re
import logging

def parse_window_parameter(window: str) -> tuple[int, str]:
    """
    Parse the window parameter to ensure it is a valid value and returns the corresponding number and unit.

    Supported values: Any number followed by  'H' (hour), 'D' (day), 'W' (week)
    Note: M and Y are unsupported by to_timedelta() function in pandas. We could remedy this by converting the window to days and then filtering the data accordingly.
    """
    logger = logging.getLogger("parse_window_parameter")

    pattern = r'^(\d+)([HDW])$'
    match = re.match(pattern, window)

    if match:
        number, unit = match.groups()
        return int(number), unit
    
    else:
        logger.error(f"Invalid window parameter: {window}. Supported format is a number followed by H, D, W")
        raise ValueError(f"Invalid window parameter: {window}. Supported format is a number followed by H, D, W")