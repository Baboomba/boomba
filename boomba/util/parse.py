from collections.abc import Iterable
from datetime import datetime
import re
from typing import Optional


def to_snake_case(string: str) -> str:
    result = re.sub(r'([a-z])([A-Z])', r'\1_\2', string)
    return result.lower()


def to_date_format(format: str, valid_specials: Iterable=None) -> str:
    """
    Converts a given date format string (e.g., 'YYYY-MM-DD HH:mm:ss') to 
    a format recognized by Python's strftime (e.g., '%Y-%m-%d %H:%M:%S').
    
    Args
    ----
    date_format : str
        The date format string containing custom date placeholders like 
        'YYYY', 'MM', 'DD', etc., that need to be converted.
    
    Returns
    -------
    str
        The date format string converted to the Python strftime format.
    
    Raises
    ------
    ValueError
        If the provided date format contains unsupported or invalid characters.
    
    Example
    -------
    >>> to_date_format('YYYY-MM-DD HH:mm:ss')
    '%Y-%m-%d %H:%M:%S'
    """
    date_map = {
        'YYYY': '%Y',
        'MM': '%m',
        'DD': '%d',
        'HH': '%H',
        'mm': '%M',
        'ss': '%S'
    }
    
    if valid_specials is None:
        valid_specials = "-_ "
    
    check = format
    
    # Remove map key
    for key in date_map:
        if key in check:
            index = check.find(key)
            check = check[:index] + check[index + len(key):]
    
    # Remove allowed special characters
    for char in valid_specials:
        check = check.replace(char, "")
    
    # If there are any remaining characters, raise an error
    if check:
        raise ValueError(
            f"Invalid format found in the date_format "
            f"of configuration: {check}"
        )
            
    for k, v in date_map.items():
        format = format.replace(k, v)
    
    return format


def parse_date(
        date_str: str,
        format: str,
        valid_specials: Iterable=None,
        time_only: bool=False
    ) -> Optional[datetime]:
    '''
    Converts a string in YYYYMMDD HHmmss format to a datetime object.

    Args
    ----
    - date_str : The date string. For example: 20250101, 16:20:00
    - format : The date format in YYYYMMDD HHmmss style
    - valid_specials : Allowed special characters. Default is '-', '_', ' '
    - time_only : Returns only the time without the year, month, and day. Default is False
    
    Example
    -------
    >>> date = parse_date('16:20:00', 'HH:mm:ss', ':')
    >>> print(date)
    ... datetime.time(16, 20)

    See also
    --------
    to_date_format
    '''
    if date_str is not None:
        format = to_date_format(format, valid_specials)
        new_date = datetime.strptime(date_str, format)
    
        if time_only:
            return new_date.time()
        
        return new_date
    
    return None


def parse_boolean(key: str) -> bool:
    """
    Parses and validates the boolean field to determine the file system type.
    
    Args
    ----
    - key(str) : The field to check
    
    Returns
    -----
    - bool: True if the file system is remote, False if local.
    
    Raises:
    - ValueError: If the 'is_remote' field is not set to 'true' or 'false'.
    """
    valid_values = {'true', 'false'}
    key = key.lower()
    
    if key not in valid_values:
        raise ValueError(
            f"'{key}' in the configuration must be "
            f"one of {', '.join(valid_values)}."
        )
    return key == 'true'