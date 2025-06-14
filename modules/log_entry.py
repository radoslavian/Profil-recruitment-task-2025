from enum import Enum
import datetime


class LogLevelValues(Enum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


DEFAULT_LOG_LEVEL = LogLevelValues.DEBUG


class LogEntry:
    def __init__(self,
                 date: datetime.datetime,
                 log_level: LogLevelValues,
                 message: str):
        self.date = date
        self.log_level = log_level
        self.message = message

    def __repr__(self):
        date = self.date.isoformat()
        return f"LogEntry(date={date}, " \
            f"log_level='{self.log_level}', " \
            f"message='{self.message}')"
