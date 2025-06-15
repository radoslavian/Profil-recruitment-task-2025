from abc import ABC, abstractmethod
import datetime
from modules.log_entry import LogEntry, LogLevelValue
from typing import List, TextIO
import os
import json


class Handler(ABC):
    @abstractmethod
    def __init__(self):
        self._create_log_if_non_existent()

    @abstractmethod
    def persist_log(self, entry: LogEntry):
        pass

    @abstractmethod
    def retrieve_all_logs(self) -> List[LogEntry]:
        pass

    @abstractmethod
    def _create_log_if_non_existent(self):
        pass


class FileHandler(Handler):
    def __init__(self, filename):
        self.filename = filename
        super(FileHandler, self).__init__()

    def _create_log_if_non_existent(self):
        if not os.path.exists(self.filename):
            with open(self.filename, "w") as f:
                f.write("")

    def persist_log(self, entry: LogEntry):
        log_line = f"{entry.date.isoformat()} {entry.level} {entry.message}\n"
        with open(self.filename, "a") as f:
            f.write(log_line)

    def retrieve_all_logs(self) -> List[LogEntry]:
        try:
            with open(self.filename, "r") as file_handle:
                log_entries = self._read_entries_from_file(file_handle)
        except (FileNotFoundError, ValueError):
            return []
        return log_entries

    def _read_entries_from_file(self, file_handle: TextIO) -> List[LogEntry]:
        return [self._read_line_into_log_entry(line)
                for line in filter(None, file_handle.readlines())]

    @staticmethod
    def _read_line_into_log_entry(line: str) -> LogEntry:
        parts = line.strip().split(" ", 2)
        date = datetime.datetime.fromisoformat(parts[0])
        level = LogLevelValue[parts[1]]
        msg = parts[2]
        if len(parts) == 3:
            log_entry = LogEntry(date=date, level=level, msg=msg)
        else:
            # for the sake of safety
            raise ValueError
        return log_entry


class JsonHandler(Handler):
    def __init__(self, filepath):
        self.filepath = filepath
        super(JsonHandler, self).__init__()

    def _create_log_if_non_existent(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w") as file_in:
                json.dump([], file_in)

    def persist_log(self, entry: LogEntry):
        pass

    def retrieve_all_logs(self) -> List[LogEntry]:
        pass


class CSVHandler(Handler):
    pass


class SQLiteHandler(Handler):
    pass
