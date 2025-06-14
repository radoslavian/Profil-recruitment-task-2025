from __future__ import annotations
from typing import Dict, List
from enum import Enum
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
                 level: LogLevelValue,
                 msg: str):
        self.date = date
        self.log_level = level
        self.message = msg

    def to_dict(self) -> Dict:
        return dict(self)

    @staticmethod
    def from_dict(entry: Dict[str, str]) -> LogEntry:
        return LogEntry(date=entry["date"],
                        level=entry["level"],
                        msg=entry["msg"])

    def __getitem__(self, key: str):
        return dict(zip(self.keys(), self.values()))[key]

    @staticmethod
    def keys() -> List[str]:
        return ["date", "level", "msg"]

    def values(self) -> List[str]:
        return [self.date, self.log_level.name, self.message]

    def __repr__(self):
        date = self.date.isoformat()
        return f"LogEntry(date={date}, " \
            f"level='{self.log_level.name}', " \
            f"msg='{self.message}')"
