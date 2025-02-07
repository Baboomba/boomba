from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta, time
from enum import Enum
from pathlib import Path
import time as Time
from typing import List, Optional, Deque, Dict, Tuple

from boomba.core.config import Config, Conf
from boomba.core.constants import LOOP_INTERVAL, PIPELINE_DIR
from boomba.core.etl import Loader
from boomba.core.metadata import MetaDataManager
from boomba.util.parse import parse_date


__all__ = ['Job', 'register']

_metadata = MetaDataManager()


class WeekDay(Enum):
    mon = 0
    tue = 1
    wed = 2
    thu = 3
    fri = 4
    sat = 5
    sun = 6


class CronParser:
    """
    A class to parse cron expressions into individual components.

    This class takes a cron expression and splits it into its components 
    (minute, hour, day, month, and weekday). It validates the input values 
    against the allowed ranges and converts the expression into a structured 
    dictionary of possible values for each time unit.

    Attributes
    ----------
    RANGES : dict
        A dictionary defining the allowed range of values for each time unit:
        - `minute`: 0-59
        - `hour`: 0-23
        - `day`: 1-31
        - `month`: 1-12
        - `weekday`: 0-6 (Monday = 0, Sunday = 6)
    
    Methods
    -------
    parse(expr: str) -> dict:
        Parses a cron expression into a dictionary of valid values for each time unit.

    _parse_field(field: str, unit: str) -> List[int]:
        Parses a single field of a cron expression and returns a list of valid values 
        for the specified time unit.
    """
    RANGES = {
        "minute": (0, 59),
        "hour": (0, 23),
        "day": (1, 31),
        "month": (1, 12),
        "weekday": (0, 6)
    }
    
    def _split_field(self, expr: str) -> List[str]:
        fields = expr.split()
        
        if len(fields) != 5:
            raise ValueError(
                "cron expression must have 5 of fields."
            )
        return fields
    
    def _parse_field(self, field: str, unit: str) -> List[int]:
        min_v, max_v = self.RANGES[unit]
        values = set()
        
        for part in field.split(","):
            if "-" in part:
                start, end = map(int, part.split("-"))
                values.update(range(start, end + 1))
            elif "/" in part:
                base, step = part.split("/")
                step = int(step)
                
                base_range = self._parse_field(base, unit)
                
                for v in base_range:
                    while v <= max_v:
                        values.add(v)
                        v += step
            elif part == "*":
                values.update(range(min_v, max_v + 1))
            else:
                values.add(int(part))
        
        if min(values) < min_v or max(values) > max_v:
            raise KeyError(
                f"Allowed values for '{unit}' "
                f"are between {min_v} and {max_v}"
            )
        
        return list(values)
    
    def parse(self, expr: str) -> Dict[str, List[int]]:
        fields = self._split_field(expr)
            
        return {
            unit: self._parse_field(field, unit)
            for field, unit in zip(fields, self.RANGES.keys())
        }


class Schedule:
    '''
    A class to manage scheduling.

    This class generates the next scheduled time and a list of schedules 
    for the current day. The schedule representation is based on cron expressions. 
    You can either use the cron expression itself or specify individual values, 
    but using both simultaneously will result in an error.

    Since schedule building can occur multiple times on the same day 
    (e.g., every 10 minutes), if the current day matches the schedule, 
    it may generate multiple schedules for the day. This functionality 
    is implemented in the `build()` method.

    The `parser` attribute is intended for dependency injection 
    and does not need to be modified directly.
    
    Args
    ----
    The class supports both cron-specific expressions and custom values outside the default range. 
    Cron expressions allow the following special syntax:
    - `*` (all values)
    - `/` (increments)
    - `-` (ranges)
    - `,` (multiple values)

    - `minute`: Defaults to `0`, range: `0-59`.
    - `hour`: Defaults to `0`, range: `0-23`.
    - `day`: Defaults to `*`, range: `1-31`.
    - `month`: Defaults to `*`, range: `1-12`.
    - `weekday`: Defaults to `*`, range: `0-6` (0 = Monday, 6 = Sunday).
    
    Example
    -------
    >>> schedule = Schedule(expr='0/10 1-5 3 * *')
    ... schedule = Schedule(minute='0/10', hour='1-5', day=3)
    '''
    def __init__(
        self,
        minute: Optional[int|str]=None,
        hour: Optional[int|str]=None,
        day: Optional[int|str]=None,
        month: Optional[int|str]=None,
        weekday: str=None,
        expr: str=None,
        parser: CronParser=None
    ) -> None:
        self._parser = parser or CronParser()
        
        if expr is not None and any(
            param is not None 
            for param in (minute, hour, day, month, weekday)
        ):
            raise ValueError(
                "When 'expr' is set, 'minute', 'hour', 'day', "
                "'month', and 'weekday' must not be set."
            )
        
        if expr is not None:
            fields = self._parser._split_field(expr)
            self._minute = fields[0]
            self._hour = fields[1]
            self._day = fields[2]
            self._month = fields[3]
            self._weekday = fields[4]
            self._expr = expr
        else:
            self._minute = minute or 0
            self._hour = hour or 0
            self._day = day or '*'
            self._month = month or '*'
            self._weekday = self._weekday_to_int(weekday)
            self._expr = expr
    
    def __repr__(self) -> str:
        return (
            "[SchedulerBuilder]\n"
            f"- module : {self.__module__}\n"
            f"- expr : {self.expr}\n"
            f"- weeday : {self._weekday}\n"
            f"- month : {self._month}\n"
            f"- day : {self._day}\n"
            f"- hour : {self._hour}\n"
            f"- minute : {self._minute}\n"
        )
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Schedule):
            return False
        return self.expr == other.expr
    
    @property
    def year(self) -> int:
        return datetime.today().year
    
    @property
    def expr(self) -> str:
        if self._expr is None:
            return (
                f"{self._minute} "
                f"{self._hour} "
                f"{self._day} "
                f"{self._month} "
                f"{self._weekday}"
            )
        
        return self._expr
    
    def _weekday_to_int(self, weekday: str) -> int:
        if weekday is None:
            return '*'
        
        if '/' in weekday:
            raise ValueError("The weekday cannot contain the '/' character.")
        
        for k, v in WeekDay.__members__.items():
            weekday = weekday.replace(k, str(v.value))
        
        return weekday
    
    def _is_weekday_match(self, date: datetime) -> Optional[bool]:
        valid_days = self._parser._parse_field(self._weekday, 'weekday')
        return date.weekday() in valid_days
    
    def next(self, base: datetime=None) -> datetime:
        """
        Calculates the next scheduled time based on the provided base time.

        Args
        ----
            base (datetime): The base time from which the next schedule is calculated.
                             Defaults to the current datetime if not provided.

        Returns
        -------
            datetime: The next scheduled datetime.
        """
        parsing_data = self._parser.parse(self.expr)
        
        if base is None:
            base = datetime.now()
        
        keys = {
            'minute': 0,
            'hour': 1,
            'day': 2,
            'month': 3,
            'year': 4
        }
        to_update = set()
        values = {'year': base.year}
        
        for key, id in keys.items():
            if id == (len(keys) - 1):
                if id in to_update:
                    values[key] += 1
                # year doesn't exist in parsing_data
                break
            
            parsing_data[key].sort() # ensure time sequence
            base_value = getattr(base, key)
            
            # The smallest unit is a minute.
            # Only update the value when equal to or greater than the base value, skipping other steps.
            if id == 0 or id in to_update:
                valid_value = min(
                    [v for v in parsing_data[key]
                    if v > base_value],
                    default=None
                )
            else:
                valid_value = min(
                    [v for v in parsing_data[key]
                    if v >= base_value],
                    default=None
                )
            
            if valid_value is None:
                valid_value = min(parsing_data[key])
                to_update.add(id + 1)
            
            values[key] = valid_value
        
        # when upper changed, lower reset
        if max(to_update, default=None) is not None:
            to_min = [k for k, v in keys.items() if v < max(to_update)]
        
            for k in values.keys():
                if k in to_min:
                    values[k] = min(parsing_data[k])
        
        # result
        result = base.replace(
            year=values['year'],
            month=values['month'],
            day=values['day'],
            hour=values['hour'],
            minute=values['minute'],
            second=0,
            microsecond=0
        )
        
        # check weekday
        if self._weekday != '*':
            if not self._is_weekday_match(result):
                result = self.next(result)
        
        return result
    
    def build(self) -> Optional[List[datetime]]:
        """
        Builds a list of schedules for the current day, starting from midnight.

        Returns:
            Optional[List[datetime]: A list of schedules for the current day.
            If the current day does not match the schedule, returns `None`.
        """
        today = datetime.today()
        tommorow = datetime.combine(today, time.min) + timedelta(days=1)
        
        if self._weekday != '*':
            if not self._is_weekday_match(today):
                return None
        
        next_ = self.next()
        schedule: Optional[List[datetime]] = []
        
        while True:
            if next_ >= tommorow or next_ is None:
                break
            
            schedule.append(next_)
            next_ = self.next(next_)
        
        return schedule


def _register_jobs() -> None:
    '''Force execute the schedule.py file of all pipelines to register the jobs.'''
    try:
        path = Path(PIPELINE_DIR)
        for dir in path.iterdir():
            if dir.is_dir() and dir.name != '__pycache__':
                file = dir / 'schedule.py'
                
                with open(file, 'r') as f:
                    schedule = f.read()
                exec(schedule, {}, {})
    
    except Exception as e:
        raise FileNotFoundError(str(e))


@dataclass(eq=False)
class ETLJob:
    loader: Loader
    name: str
    schedule: Schedule
    start: datetime = field(default_factory=datetime.now)
    end: datetime = field(default=None)
    completed_jobs: List[datetime] = field(default_factory=list)
    next_job: datetime = field(default=None)
    today_jobs: List[datetime] = field(default_factory=list)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ETLJob):
            return False
        return (
            self.loader == other.loader and
            self.schedule == other.schedule
        )
        
        
class JobMeta(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
        

class Job(metaclass=JobMeta):

    def __init__(
        self,
        conf: Config=Conf,
        schedule: Schedule=None,
        metadata: MetaDataManager=_metadata
    ) -> None:
        self._conf = conf
        self._schedule = schedule or Schedule
        self.job_list: List[ETLJob] = []
        self._metadata = metadata
    
    def __str__(self) -> str:
        return f"Job with {len(self.job_list)} jobs"
    
    def __repr__(self) -> str:
        return (
            f"- jobs : {len(self.job_list)}\n"
            f"- job_list : {[j.name for j in self.job_list]}\n"
        )
    
    @property
    def now(self) -> datetime:
        return datetime.now()
    
    @property
    def today(self) -> datetime:
        return datetime.combine(
            date.today(),
            datetime.min.time()
        )
    
    def _filter_active_jobs(self, job_list: List[ETLJob]) -> List[ETLJob]:
        '''Filter jobs that are active based on their start and end dates.'''
        new_list: List[ETLJob] = []
        
        for job in job_list:
            start_ = job.start is not None
            end_ = job.end is not None
            
            if start_ and not end_:
                if job.start > self.now:
                    continue
            
            if not start_ and end_:
                if job.end < self.now:
                    continue
            
            if all((start_, end_)):
                if job.start > self.now and job.end < self.now:
                    continue
            
            new_list.append(job)
        
        return new_list
    
    def _initiate_schedule(self, job_list: List[ETLJob]) -> List[ETLJob]:
        job_list = self._filter_active_jobs(job_list)
        self._metadata.init_schdule(self.now)
        
        new_list: List[ETLJob] = []
        for job in job_list:
            schedule = job.schedule.build()
            
            if schedule:
                job.today_jobs = schedule
                job.next_job = job.schedule.next()
                new_list.append(job)
                
        return new_list
    
    def _initiate_queue(
        self,
        job_list: List[ETLJob]
    ) -> Deque[Tuple[Loader, datetime, str]]:
        '''
        Initializes a job queue based on the given job list.
    
        The queue is populated with tuples consisting of the loader, scheduled time, 
        and job name, sorted by scheduled time.
        
        Returns
        -------
        Deque[Tuple[Loader, datetime]]
        A queue of tuples, each containing a loader, scheduled time, and job name, 
        sorted by scheduled time.
        '''
        tmp_list: List[Tuple[Loader, datetime, str]] = []
        for job in job_list:
            for t in job.today_jobs:
                tmp_list.append((job.loader, t, job.name))
                
                self._metadata.save_schedule(
                    scheduled_at=t,
                    job_name=job.name
                )
                
        tmp_list.sort(key=lambda x: x[1]) # to ensure time sequence
        q = deque(tmp_list)
        self._metadata.save_queue(q)
        return q
    
    def _print_status(self) -> None:
        n = len(self.job_list)
        job_names = [job.name for job in self.job_list]
        print(
            f"Registered {n} jobs in the system. "
            f"The job List={', '.join(job_names)}"
        )
    
    def register(
        self,
        loader: Loader,
        name: str,
        minute: int=None,
        hour: int=None,
        day: int=None,
        month: int=None,
        weekday: str=None,
        expr: str=None,
        start: str=None,
        end: str=None,
    ) -> None:
        schedule = self._schedule(
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            weekday=weekday,
            expr=expr
        )
        format = self._conf.job_date_format
        start_ = parse_date(start, format)
        end_ = parse_date(end, format)
        
        job = ETLJob(
            loader=loader,
            name=name,
            schedule = schedule,
            start=start_,
            end=end_
        )
        
        for j in self.job_list:
            if name == j.name:
                raise ValueError(f"Duplicate job name. {name}")
        
        if job not in self.job_list:
            self.job_list.append(job)
            self._metadata.save_job(
                job_name=job.name,
                registered_at=datetime.now(),
                start_date=job.start,
                end_date=job.end,
                cron_expression=expr
            )
        else:
            print(f"[Warning] '{name}' is already in the list.")
    
    def run(self) -> None:
        init_date = None
        _register_jobs()
        self._print_status()

        while True:
            Time.sleep(LOOP_INTERVAL)
            
            # initiate job every day(or when run first)
            if init_date is None or init_date.day != self.now.day:
                init_date = self.now
                job_list = self._initiate_schedule(self.job_list)
                job_queue = self._initiate_queue(job_list)
            
            if not job_queue:
                print(f'all jobs have been done... {self.now}')
                continue
            
            if job_queue[0][1] <= self.now:
                job = job_queue.popleft()
                
                try:
                    inst: Loader = job[0]() # run Loader subclass
                    
                    for i, j in enumerate(job_list):
                        if j.name == job[2]:
                            job_list[i].completed_jobs.append(job[1])
                            job_list[i].next_job = j.schedule.next()
                            print(f'job completed... {j.name}')
                    
                    # save the result of the job execution into the default database
                    self._metadata.save_schedule(
                        scheduled_at=job[1],
                        job_name=job[2],
                        executed_at=datetime.now(),
                        is_completed=True
                    )
                    self._metadata.save_dir(
                        pipe_name=inst.pipe_name,
                        collection=inst.collection,
                        job_name=job[2]
                    )
                    self._metadata.save_path(
                        file_name=inst.file_name,
                        pipe_name=inst.pipe_name,
                        collection=inst.collection,
                        scheduled_at=job[1]
                    )
                    self._metadata.save_queue(job_queue) # renew the table of queue
                    
                except Exception as e:
                    pass
                

def register(
    loader: Loader,
    name: str,
    minute: int=None,
    hour: int=None,
    day: int=None,
    month: int=None,
    weekday: str=None,
    expr: str=None,
    start: str=None,
    end: str=None,
) -> None:
    '''API for user convenience when registering a job'''
    job = Job()
    job.register(
        loader=loader,
        name=name,
        minute=minute,
        hour=hour,
        day=day,
        month=month,
        weekday=weekday,
        expr=expr,
        start=start,
        end=end
    )