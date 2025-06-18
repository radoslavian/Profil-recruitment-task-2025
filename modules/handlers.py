from abc import ABC, abstractmethod
from typing import List, TextIO, Dict
import datetime
import os
import json
import csv
import sqlite3
from modules.log_entry import LogLevelValue, LogEntry


class Handler(ABC):
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
    def __init__(self, filename: str):
        self.filename = filename
        super(FileHandler, self).__init__()

    def _create_log_if_non_existent(self):
        if not os.path.exists(self.filename):
            with open(self.filename, "w") as f:
                f.write("")

    def persist_log(self, entry: LogEntry):
        log_line = f"{entry.date} {entry.level} {entry.message}\n"
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
    def __init__(self, filepath: str):
        self.filepath = filepath
        super(JsonHandler, self).__init__()

    def _create_log_if_non_existent(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w") as file_in:
                json.dump([], file_in)

    def persist_log(self, entry: LogEntry):
        log_entries = []
        try:
            if self._nonempty_file_exists():
                log_entries = self._load_entries()
        except (json.JSONDecodeError, FileNotFoundError):
            log_entries = []
        log_entries = [*log_entries, entry.to_dict()]
        self._save_entries(log_entries)

    def _save_entries(self, log_entries: List[Dict]):
        with open(self.filepath, 'w', ) as f_out:
            json.dump(log_entries, f_out, indent=4)

    def _load_entries(self):
        with open(self.filepath, "r") as f_in:
            return json.load(f_in)

    def _nonempty_file_exists(self) -> bool:
        return (os.path.exists(self.filepath)
                and os.path.getsize(self.filepath) > 0)

    def retrieve_all_logs(self) -> List[LogEntry]:
        log_entries = []
        try:
            with open(self.filepath, "r") as file_in:
                loaded_log_entries = json.load(file_in)
                for entry in loaded_log_entries:
                    log_entry = LogEntry.from_dict(entry)
                    log_entries.append(log_entry)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            return []
        return log_entries


class CSVHandler(Handler):
    def __init__(self, filepath: str):
        self.file_path = filepath
        super(CSVHandler, self).__init__()

    def _create_log_if_non_existent(self):
        if not os.path.exists(self.file_path) or \
           os.path.getsize(self.file_path) == 0:
            with open(self.file_path, "w", newline="", ) as f:
                writer = csv.writer(f)
                writer.writerow(["date", "level", "message"])

    def persist_log(self, entry: LogEntry):
        log_entry = entry.to_dict()
        log_entry_row = [log_entry["date"],
                         log_entry["level"],
                         log_entry["message"]]
        self._save_entry(log_entry_row)

    def _save_entry(self, log_entry_row: List[str]):
        with open(self.file_path, "a", newline="", ) as fh:
            writer = csv.writer(fh)
            writer.writerow(log_entry_row)

    def retrieve_all_logs(self) -> List[LogEntry]:
        try:
            log_entries = self._load_entries()
        except FileNotFoundError:
            return []
        return log_entries

    def _load_entries(self) -> List[LogEntry]:
        with open(self.file_path, 'r', newline='', ) as fh:
            reader = csv.DictReader(fh)
            log_entries = [LogEntry.from_dict(row) for row in reader]

        return log_entries


class SQLiteHandler(Handler):
    def __init__(self, database_path: str, table_name: str = "log"):
        self.db_path = database_path
        self.table_name = table_name
        super(SQLiteHandler, self).__init__()

    def _create_log_if_non_existent(self):
        with self._get_conn() as connection:
            cursor = connection.cursor()
            create_table_sql = f'''
                CREATE TABLE {self.table_name} (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL
                )
            '''
            cursor.executescript(create_table_sql)

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def persist_log(self, entry: LogEntry):
        pass

    def retrieve_all_logs(self) -> List[LogEntry]:
        pass
