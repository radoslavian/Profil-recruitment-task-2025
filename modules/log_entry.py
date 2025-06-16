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
                 date: str,
                 level: str,
                 msg: str):
        self._date = datetime.datetime.fromisoformat(date)
        self._log_level = LogLevelValue[level]
        self._message = msg

    def to_dict(self) -> Dict:
        return dict(self)

    @staticmethod
    def from_dict(entry: Dict[str, str]) -> LogEntry:
        return LogEntry(date=entry["date"],
                        level=entry["level"],
                        msg=entry["message"])

    def __getitem__(self, key: str):
        return dict(zip(self.keys(), self.values()))[key]

    @staticmethod
    def keys() -> List[str]:
        return ["date", "level", "message"]

    def values(self) -> List[str]:
        return [self.date, self.level, self.message]

    def __repr__(self):
        return f"LogEntry(date={self.date}, " \
            f"level='{self._log_level.name}', " \
            f"msg='{self._message}')"

    date = property(lambda self: self._date.isoformat())
    level = property(lambda self: self._log_level.name)
    message = property(lambda self: self._message)
