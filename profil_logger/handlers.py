import csv
import datetime
import json
import os
import sqlite3
from abc import ABC, abstractmethod
from typing import Dict, IO, List, TextIO, Tuple
from profil_logger.log_entry import LogEntry, LogLevelValue


class Handler(ABC):
    def __init__(self):
        self._create_log_if_non_existent()

    @abstractmethod
    def persist_log(self, entry: LogEntry):
        pass

    @abstractmethod
    def retrieve_all_logs(self) -> List[LogEntry]:
        pass

    def _create_log_if_non_existent(self):
        pass


class FileIOHandler(Handler):
    """
    Generic class for inheriting classes using file input-output.
    """
    def __init__(self, filepath: str):
        self.filepath = filepath
        super(FileIOHandler, self).__init__()

    def _get_file_handle(self, mode: str, **kwargs) -> IO:
        return open(self.filepath, mode, **kwargs)


class FileHandler(FileIOHandler):
    def _create_log_if_non_existent(self):
        if not os.path.exists(self.filepath):
            with self._get_file_handle("w") as fh:
                fh.write("")

    def persist_log(self, entry: LogEntry):
        log_line = f"{entry['date']} {entry['level']} {entry['message']}\n"
        with self._get_file_handle("a") as fh:
            fh.write(log_line)

    def retrieve_all_logs(self) -> List[LogEntry]:
        try:
            with self._get_file_handle("r") as fh:
                log_entries = self._read_entries_from_file(fh)
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


class JsonHandler(FileIOHandler):
    def _create_log_if_non_existent(self):
        if not os.path.exists(self.filepath):
            with self._get_file_handle("w") as fh:
                json.dump([], fh)

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
        with self._get_file_handle("w") as fh:
            json.dump(log_entries, fh, indent=4)

    def _load_entries(self):
        with self._get_file_handle("r") as fh:
            return json.load(fh)

    def _nonempty_file_exists(self) -> bool:
        return (os.path.exists(self.filepath)
                and os.path.getsize(self.filepath) > 0)

    def retrieve_all_logs(self) -> List[LogEntry]:
        log_entries = []
        try:
            with self._get_file_handle("r") as fh:
                loaded_log_entries = json.load(fh)
                for entry in loaded_log_entries:
                    log_entry = LogEntry.from_dict(entry)
                    log_entries.append(log_entry)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            return []
        return log_entries


class CSVHandler(FileIOHandler):
    def _create_log_if_non_existent(self):
        if not os.path.exists(self.filepath) or \
           os.path.getsize(self.filepath) == 0:
            with self._get_file_handle("w", newline="") as fh:
                writer = csv.writer(fh)
                writer.writerow(["date", "level", "message"])

    def persist_log(self, entry: LogEntry):
        log_entry = entry.to_dict()
        log_entry_row = [log_entry["date"],
                         log_entry["level"],
                         log_entry["message"]]
        self._save_entry(log_entry_row)

    def _save_entry(self, log_entry_row: List[str]):
        with self._get_file_handle("a", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(log_entry_row)

    def retrieve_all_logs(self) -> List[LogEntry]:
        try:
            log_entries = self._load_entries()
        except FileNotFoundError:
            return []
        return log_entries

    def _load_entries(self) -> List[LogEntry]:
        with self._get_file_handle("r", newline='') as fh:
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
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL
                )
            '''
            cursor.executescript(create_table_sql)

    def persist_log(self, entry: LogEntry):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            sql_query = (f"INSERT INTO {self.table_name} (timestamp, "
                         f"level, message) VALUES ('{entry['date']}', "
                         f"'{entry['level']}', '{entry['message']}')")

            cursor.executescript(sql_query)

    def retrieve_all_logs(self) -> List[LogEntry]:
        try:
            log_entries = self._fetch_resulting_rows()
        except (sqlite3.Error, ValueError):
            return []
        return log_entries

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def _fetch_resulting_rows(self) -> List[LogEntry]:
        retrieval_statement = (f"SELECT timestamp, level, message FROM "
                               f"{self.table_name} ORDER BY timestamp ASC")

        with self._get_conn() as connection:
            cursor = connection.cursor()
            cursor.execute(retrieval_statement)
            entry_rows = cursor.fetchall()

        fetched_entries = self._fetch_log_entries(entry_rows)
        return fetched_entries

    def _fetch_log_entries(self,
                           fetched_rows: List[Tuple]) -> List[LogEntry]:
        return [LogEntry(date=datetime.datetime.fromisoformat(row[0]),
                         level=LogLevelValue[row[1]],
                         msg=row[2])
                for row in fetched_rows]
