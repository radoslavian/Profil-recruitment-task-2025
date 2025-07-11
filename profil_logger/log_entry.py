from __future__ import annotations
import datetime
from enum import Enum
from typing import Dict, List


class LogLevelValue(Enum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


class LogEntry:
    def __init__(self,
                 date: datetime.datetime,
                 level: LogLevelValue,
                 msg: str):
        self._date = date
        self._log_level = level
        self._message = msg

    def to_dict(self) -> Dict[str, str]:
        return dict(self)

    @staticmethod
    def from_dict(entry: Dict[str, str]) -> LogEntry:
        date = datetime.datetime.fromisoformat(entry["date"])
        level = LogLevelValue[entry["level"]]
        return LogEntry(date=date,
                        level=level,
                        msg=entry["message"])

    def __getitem__(self, key: str):
        return dict(zip(self.keys(), self.values()))[key]

    @staticmethod
    def keys() -> List[str]:
        return ["date", "level", "message"]

    def values(self) -> List[str]:
        return [self.date.isoformat(), self.level.name, self.message]

    def __repr__(self):
        return f"LogEntry(date={self['date']}, " \
            f"level='{self['level']}', " \
            f"message='{self.message}')"

    date = property(lambda self: self._date)
    level = property(lambda self: self._log_level)
    message = property(lambda self: self._message)
