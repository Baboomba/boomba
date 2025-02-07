from datetime import datetime, date
from typing import List
from typing import Optional, Tuple, Deque

from sqlalchemy import (
    Integer,
    String,
    DateTime,
    Date,
    Boolean,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
    Session
)

from boomba.core.config import Conf
from boomba.core.constants import BASE_DATA_FORMAT
from boomba.core.db import Connector
from boomba.core.etl import Loader

__all__ = [
    'Base'
    'JobInfo',
    'ScheduleInfo',
    'DataDirectory',
    'DataPath',
    'SaveMetaData'
]

_connector = Connector(Conf.base_db, Conf)


class Base(DeclarativeBase):
    pass


class JobInfo(Base):
    __tablename__ = "job_info"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    job_name: Mapped[str] = mapped_column(String(32), unique=True)
    registered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    cron_expression: Mapped[str] = mapped_column(String(100))
    
    schedule_info: Mapped[List["ScheduleInfo"]] = relationship(
        "ScheduleInfo", back_populates="job_info", cascade='save-update'
    )
    data_directory: Mapped["DataDirectory"] = relationship(
        "DataDirectory", back_populates="job_info", uselist=False, cascade='save-update'
    )
    
    def __repr__(self) -> str:
        return f"JobInfo(id={self.id!r}, name={self.job_name!r})"


class ScheduleInfo(Base):
    __tablename__ = "schedule_info"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("job_info.id"))
    scheduled_at: Mapped[datetime] = mapped_column(DateTime)
    executed_at: Mapped[datetime] = mapped_column(DateTime, default=None, nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    path_id: Mapped[Optional[int]] = mapped_column(ForeignKey("data_path.id"))
    
    job_info: Mapped["JobInfo"] = relationship(
        "JobInfo", back_populates="schedule_info", cascade='save-update'
    )
    data_path: Mapped["DataPath"] = relationship(
        "DataPath", back_populates="schedule_info", uselist=False, cascade='save-update'
    )
    
    __table_args__ = (
        UniqueConstraint('job_id', 'scheduled_at', name='_job_schedule_uc'),
    )
    
    def __repr__(self) -> str:
        return (
            f"ScheduleInfo(id={self.id!r}, "
            f"job_name={self.job_id!r}), "
            f"scheduled_at={self.scheduled_at!r}, "
            f"executed_at={self.executed_at})"
        )

  
class DataDirectory(Base):
    __tablename__ = 'data_directory'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    pipe_name: Mapped[str] = mapped_column(String(32))
    collection: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    job_id: Mapped[Optional[int]] = mapped_column(ForeignKey("job_info.id"))
    
    data_path: Mapped[List["DataPath"]] = relationship(
        "DataPath", back_populates="data_directory", cascade='save-update'
    )
    job_info: Mapped["JobInfo"] = relationship(
        "JobInfo", back_populates="data_directory", uselist=False, cascade='save-update'
    )
    
    __table_args__ = (
        UniqueConstraint('pipe_name', 'collection', name='_pipe_collection_uc'),
    )
    
    def __repr__(self) -> str:
        return (
            f"DataPath(id={self.id!r}, "
            f"file_name={self.pipe_name!r}, "
            f"file_type={self.collection!r})"
        )


class DataPath(Base):
    __tablename__ = 'data_path'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    dir_id: Mapped[int] = mapped_column(ForeignKey('data_directory.id'))
    file_name: Mapped[str] = mapped_column(String(32))
    file_type: Mapped[str] = mapped_column(String(32))
    update_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    data_directory: Mapped["DataDirectory"] = relationship(
        "DataDirectory", back_populates="data_path", cascade='save-update'
    )
    schedule_info: Mapped[List["ScheduleInfo"]] = relationship(
        "ScheduleInfo", back_populates="data_path", cascade='save-update', uselist=True
    )
    
    __table_args__ = (
        UniqueConstraint('dir_id', 'file_name', name='_dir_file_uc'),
    )
    
    def __repr__(self) -> str:
        return (
            f"DataPath(id={self.id!r}, "
            f"file_name={self.file_name!r}, "
            f"file_type={self.file_type!r})"
        )


class QueueInfo(Base):
    __tablename__ = 'queue_info'
    
    queue_no: Mapped[int] = mapped_column(primary_key=True)
    job_name: Mapped[str] = mapped_column(String(32))
    scheduled_at: Mapped[datetime] = mapped_column(DateTime)
    
    def __repr__(self) -> str:
        return (
            f"QueueInfo(queue_no={self.queue_no}, "
            f"job_name={self.job_name}, scheduled_at={self.scheduled_at})"
        )


class MetaDataManager:
    
    def __init__(self, connector: Connector=_connector) -> None:
        self._connector = connector
    
    def _save_session(func):
        def wrapper(self, *args, **kwargs):
            try:
                engine = self._connector.engine
                with sessionmaker(engine)() as session:
                    obj = func(self, session, *args, **kwargs)
                    session.commit()
                    return obj
                
            except Exception as e:
                if session:
                    session.rollback()
                raise RuntimeError(str(e))
        return wrapper
    
    @_save_session
    def init_schdule(
        self,
        session: Session,
        datetime: datetime
    ) -> None:
        session.query(ScheduleInfo)\
               .filter(ScheduleInfo.scheduled_at > datetime)\
               .delete()
    
    @_save_session
    def save_job(
        self,
        session: Session,
        job_name: str,
        registered_at: datetime,
        cron_expression: str,
        start_date: str=None,
        end_date: str=None
    ) -> JobInfo:
        job = session.query(JobInfo)\
                     .filter_by(job_name=job_name)\
                     .first()
        
        if job is None:
            if start_date is None:
                start_date = datetime.now()
                
            job = JobInfo(
                job_name=job_name,
                registered_at=registered_at,
                start_date=start_date,
                end_date=end_date,
                cron_expression=cron_expression
            )
            session.add(job)
        
        return job
    
    @_save_session
    def save_schedule(
        self,
        session: Session,
        scheduled_at: datetime,
        job_name: str,
        executed_at: datetime=None,
        is_completed: bool=None,
    ) -> ScheduleInfo:
        job_info = session.query(JobInfo)\
                          .filter_by(job_name=job_name).first()
        schedule = session.query(ScheduleInfo)\
                          .filter_by(job_id=job_info.id, scheduled_at=scheduled_at)\
                          .first()
        
        if schedule is None:
            schedule = ScheduleInfo(
                scheduled_at=scheduled_at,
                job_info=job_info
            )
            session.add(schedule)
        else:
            schedule.is_completed = is_completed
            schedule.executed_at = executed_at
            session.add(schedule)
        
        return schedule
    
    @_save_session    
    def save_dir(
        self,
        session: Session,
        pipe_name: str,
        collection: str,
        job_name: str
    ) -> DataDirectory:
        dir = session.query(DataDirectory)\
                     .filter_by(pipe_name=pipe_name, collection=collection)\
                     .first()
        
        if dir is None:
            job_info = session.query(JobInfo)\
                              .filter_by(job_name=job_name).first()
            dir = DataDirectory(
                pipe_name=pipe_name,
                collection=collection,
                job_info=job_info
            )
            session.add(dir)
        
        return dir
    
    @_save_session
    def save_path(
        self,
        session: Session,
        file_name: str,
        pipe_name: str,
        collection: str,
        scheduled_at: str,
        file_type: str=None
    ) -> DataPath:
        data_dir: DataDirectory = session.query(DataDirectory)\
                          .filter_by(pipe_name=pipe_name, collection=collection)\
                          .first()
        schedule_info = session.query(ScheduleInfo)\
                               .filter_by(job_id=data_dir.job_id, scheduled_at=scheduled_at)\
                               .first()
        path = session.query(DataPath)\
                      .filter_by(dir_id=data_dir.id, file_name=file_name)\
                      .first()
        
        if path:
           path.updated_at = datetime.now()
           path.update_count += 1
           path.schedule_info.append(schedule_info)
        else:
            if file_type is None:
                file_type = BASE_DATA_FORMAT
            
            path = DataPath(
                file_name=file_name,
                file_type=file_type,
                dir_id=data_dir.id,
                schedule_info=[schedule_info]
            )
        
        session.add(path)
        return path
    
    @_save_session
    def save_queue(
        self,
        session: Session,
        job_queue: Deque[Tuple[Loader, datetime, str]]
    ) -> None:
        '''
        Args
        ----
        - job_list(str, str) : a list of a pair of 'scheduled_at', and 'job_name'
        '''
        session.query(QueueInfo).delete()
        
        for i, (_, scheduled_at, job_name) in enumerate(job_queue):
            queue = QueueInfo(queue_no=i+1, scheduled_at=scheduled_at, job_name=job_name)
            session.add(queue)