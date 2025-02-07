from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import List


class PeriodGenerator:
    """
    A class for generating dates within a specific period. Returns a list of dates.

    Parameters
    ---
    - start : The start date (string)
    - end : The end date (string)
    - format : The input date format

    Example
    ---
    >>> pgen = PeriodGenerator('2020-01-01', '2020-03-01', '%Y-%m-%d')
    >>> pgen.date_list
    ['2020-01-01', '2020-02-01', '2020-03-01']
    """
    UNIT_FORMAT_MAP = {
        '%d': 'day',
        '%m': 'month',
        '%Y': 'year',
    }

    def __init__(self, start: str, end: str, format: str) -> None:
        self.format = format
        self.unit = self._parse_unit()
        self.start = self._parse_date(start)
        self.end = self._parse_date(end)

        self._validate_input()
        self.date_list = self._generate_date_list()

    def _parse_date(self, date_str: str) -> datetime:
        try:
            return datetime.strptime(date_str, self.format)
        except ValueError:
            raise ValueError(f"Invalid date '{date_str}' for format '{self.format}'.")

    def _parse_unit(self) -> str:
        for key, unit in self.UNIT_FORMAT_MAP.items():
            if key in self.format:
                return unit
        raise ValueError(f"Invalid format '{self.format}'. Supported keys are {list(self.UNIT_FORMAT_MAP.keys())}.")

    def _validate_input(self) -> None:
        if self.start > self.end:
            raise ValueError("Start date must be before or equal to end date.")

    def _generate_date_list(self) -> List[str]:
        date_list = []
        current_date = self.start

        while current_date <= self.end:
            date_list.append(current_date.strftime(self.format))
            current_date += self._get_relativedelta()

        return date_list

    def _get_relativedelta(self) -> relativedelta:
        unit_to_delta = {
            'day': relativedelta(days=1),
            'month': relativedelta(months=1),
            'year': relativedelta(years=1),
        }
        return unit_to_delta[self.unit]