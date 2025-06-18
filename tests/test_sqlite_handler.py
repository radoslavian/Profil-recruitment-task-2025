from unittest import TestCase
from unittest.mock import patch, MagicMock
from modules.handlers import SQLiteHandler
from .test_data import fake_log_entry


@patch("sqlite3.connect")
class LogHandler(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.database_path = "/path/to/database.sqlite"
        cls.table_name = "database_log"
        cls.create_database_sql = f"""
        CREATE TABLE {cls.table_name} (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL
                )
        """
        cls.add_row_sql = ("INSERT INTO {table_name} (timestamp, level, "
                           "message) VALUES ('{entry.date}', "
                           "'{entry.level}', '{entry.message}')")

        number_of_entries = range(0, 2)
        cls.log_entries = [fake_log_entry()[1] for i in number_of_entries]

    def test_connecting_to_database(self, sqlite_connect):
        SQLiteHandler(self.database_path)
        sqlite_connect.assert_called_once_with(self.database_path)

    def test_table_creation(self, connect_mock):
        mock_cursor = self.get_mock_db_cursor(connect_mock)
        SQLiteHandler(self.database_path, self.table_name)

        expected_output = self.create_database_sql.replace(" ", "")
        received_output = mock_cursor.executescript.call_args[0][0]\
                                                   .replace(" ", "")

        self.assertEqual(expected_output, received_output)

    def test_persisting_log(self, sqlite_connect):
        mock_cursor = self.get_mock_db_cursor(sqlite_connect)
        log_entry = self.log_entries[0]
        sqlite_handler = SQLiteHandler(self.database_path, self.table_name)
        sqlite_handler.persist_log(log_entry)

        expected_output = self.add_row_sql.format(table_name=self.table_name,
                                                  entry=log_entry)
        mock_cursor.executescript.assert_any_call(expected_output)

    @staticmethod
    def get_mock_db_cursor(connect_mock):
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        connect_mock.return_value.__enter__.return_value = mock_connection

        return mock_cursor
