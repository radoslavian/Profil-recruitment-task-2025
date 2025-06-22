import datetime
from modules.handlers import Handler
from modules.log_entry import LogLevelValue, LogEntry
from typing import List


DEFAULT_LOG_LEVEL = LogLevelValue.DEBUG


class ProfilLogger:
    def __init__(self, log_handlers: List[Handler]):
        self.log_handlers = log_handlers
        self._current_log_level: LogLevelValue = DEFAULT_LOG_LEVEL

    def debug(self, message: str):
        self._log(LogLevelValue.DEBUG, message)

    def info(self, message: str):
        self._log(LogLevelValue.INFO, message)

    def warning(self, message: str):
        self._log(LogLevelValue.WARNING, message)

    def error(self, message: str):
        self._log(LogLevelValue.ERROR, message)

    def critical(self, message: str):
        self._log(LogLevelValue.CRITICAL, message)

    def set_log_level(self, log_level: LogLevelValue):
        self._current_log_level = log_level

    def _log(self, log_level: LogLevelValue, message: str):
        if self._log_level_lower_than_current(log_level):
            return

        log_entry_date = datetime.datetime.now()
        entry = LogEntry(date=log_entry_date, level=log_level, msg=message)
        self._write_to_handlers(entry)

    def _log_level_lower_than_current(self, log_level: LogLevelValue) -> bool:
        return log_level.value < self._current_log_level.value

    def _write_to_handlers(self, entry: LogEntry):
        for log_handler in self.log_handlers:
            log_handler.persist_log(entry)
