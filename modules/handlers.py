from abc import ABC, abstractmethod
from modules.log_entry import LogEntry
from typing import List
import os


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
        pass

    def retrieve_all_logs(self):
        pass


class JsonHandler(Handler):
    pass


class CSVHandler(Handler):
    pass


class SQLiteHandler(Handler):
    pass
