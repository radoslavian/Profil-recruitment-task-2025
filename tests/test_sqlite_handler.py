import datetime
import sqlite3
from typing import List, Tuple
from unittest import TestCase
from unittest.mock import MagicMock, patch
from profil_logger import LogEntry, LogLevelValue, SQLiteHandler
from tests.fake_data import fake_log_entry


@patch("sqlite3.connect")
class LogHandler(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.database_path = "/path/to/database.sqlite"
        cls.table_name = "database_log"
        cls.create_database_sql = f"""
        CREATE TABLE IF NOT EXISTS {cls.table_name} (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL
                )
        """
        cls.add_row_sql = ("INSERT INTO {table_name} (timestamp, level, "
                           "message) VALUES ('{entry[date]}', "
                           "'{entry[level]}', '{entry[message]}')")
        _, cls.log_entry = fake_log_entry()

    def test_connecting_to_database(self, sqlite_connect):
        SQLiteHandler(self.database_path)
        sqlite_connect.assert_called_once_with(self.database_path)

    def test_table_creation(self, connect_mock):
        mock_cursor = get_mock_db_cursor(connect_mock)
        SQLiteHandler(self.database_path, self.table_name)

        def normalize(text):
            return "\n".join(sql.strip() for sql in text.split("\n"))

        expected_output = normalize(self.create_database_sql)
        received_output = normalize(
            mock_cursor.executescript.call_args[0][0])

        self.assertEqual(expected_output, received_output)

    def test_persisting_log(self, sqlite_connect):
        mock_cursor = get_mock_db_cursor(sqlite_connect)
        sqlite_handler = SQLiteHandler(self.database_path, self.table_name)
        sqlite_handler.persist_log(self.log_entry)

        expected_output = self.add_row_sql.format(table_name=self.table_name,
                                                  entry=self.log_entry)
        mock_cursor.executescript.assert_any_call(expected_output)


class LogRetrieval(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.database_path = "/path/to/database.sqlite"
        cls.table_name = "database_log"
        cls.logs_retrival_query = (f"SELECT timestamp, level, message FROM"
                                   f" {cls.table_name} ORDER BY timestamp ASC")
        number_of_entries = range(0, 2)
        cls.log_entries: List[Tuple] = get_fake_entries(number_of_entries)

    def setUp(self):
        sqlite_connect = MagicMock()
        self.mock_cursor = get_mock_db_cursor(sqlite_connect)
        self.mock_cursor.fetchall.return_value = self.log_entries

        with patch("sqlite3.connect", sqlite_connect):
            self.sqlite_handler = SQLiteHandler(
                self.database_path, self.table_name)
            self.all_log_entries: List[LogEntry] = self.sqlite_handler \
                                                       .retrieve_all_logs()

    def test_logs_retrieval_query(self):
        """
        It should dispatch a query for logs retrieval.
        """
        self.mock_cursor.execute.assert_any_call(
            self.logs_retrival_query)

    def test_log_entries(self):
        """
        It should return a list of log entries retrieved from the database.
        """
        # lists of string representations of LogEntry objects
        expected_log_entries: List[str] = [
            repr(LogEntry(date=datetime.datetime.fromisoformat(entry[0]),
                          level=LogLevelValue[entry[1]],
                          msg=entry[2]))
            for entry in self.log_entries]
        received_log_entries: List[str] = [
            repr(log_entry) for log_entry in self.all_log_entries]

        self.assertEqual(expected_log_entries, received_log_entries)

    def test_sqlite3_error(self):
        """
        It should return an empty list in case of the sqlite3.Error occurence.
        """
        def fail_with_sqlite3_error(*args):
            raise sqlite3.Error

        connect_mock = self.fail_executescript(fail_with_sqlite3_error)

        with patch("sqlite3.connect", connect_mock):
            log_entries = self.sqlite_handler.retrieve_all_logs()

        self.assertFalse(log_entries)

    def test_value_error(self):
        """
        It should return an empty list in case of the ValueError occurence.
        """
        def fail_with_value_error(*args):
            raise ValueError

        connect_mock = self.fail_executescript(fail_with_value_error)

        with patch("sqlite3.connect", connect_mock):
            log_entries = self.sqlite_handler.retrieve_all_logs()

        self.assertFalse(log_entries)

    def fail_executescript(self, fail):
        connect_mock = MagicMock()
        mock_cursor = get_mock_db_cursor(connect_mock)
        mock_cursor.fetchall.return_value = self.log_entries
        mock_cursor.execute = fail

        return connect_mock


def get_mock_db_cursor(connect_mock):
    mock_cursor = MagicMock()
    mock_connection = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    connect_mock.return_value.__enter__.return_value = mock_connection

    return mock_cursor


def get_fake_entries(number_of_entries: range):
    """
     Returns a list of tuples with corresponding log data (for mocking the
    cursor.fetchall() output).
    """
    entries = []
    for i in number_of_entries:
        fake_entry = fake_log_entry()
        entries += [(fake_entry[0]["date"],
                     fake_entry[0]["level"],
                     fake_entry[0]["message"],)]
    return entries
