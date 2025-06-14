from enum import Enum
from typing import Dict, List
import datetime


class LogLevelValue(Enum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


DEFAULT_LOG_LEVEL = LogLevelValue.DEBUG


class LogEntry:
    def __init__(self,
                 date: datetime.datetime,
                 log_level: LogLevelValue,
                 message: str):
        self.date = date
        self.log_level = log_level
        self.message = message

    def to_dict(self) -> Dict:
        return dict(self)

    def __getitem__(self, key: str):
        return dict(zip(self.keys(), self.values()))[key]

    @staticmethod
    def keys() -> List[str]:
        return ["date", "level", "msg"]

    def values(self):
        return [self.date.isoformat(), self.log_level.name, self.message]

    def __repr__(self):
        date = self.date.isoformat()
        return f"LogEntry(date={date}, " \
            f"level='{self.log_level.name}', " \
            f"msg='{self.message}')"
