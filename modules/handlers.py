from abc import ABC, abstractmethod
from modules.log_entry import LogEntry
from typing import List


class Handler(ABC):
    @abstractmethod
    def persist_log(self, entry: LogEntry):
        pass

    @abstractmethod
    def retrieve_all_logs(self) -> List[LogEntry]:
        pass


class FileHandler(Handler):
    pass


class JsonHandler(Handler):
    pass


class CSVHandler(Handler):
    pass


class SQLiteHandler(Handler):
    pass
