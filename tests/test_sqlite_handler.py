from unittest import TestCase
from unittest.mock import patch, MagicMock
from modules.handlers import SQLiteHandler
import re


class LogAccessCreation(TestCase):
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

    def test_connecting_to_database(self):
        with patch("sqlite3.connect") as sqlite_connect:
            SQLiteHandler(self.database_path)
            sqlite_connect.assert_called_once_with(self.database_path)

    def test_table_creation(self):
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        connect_mock = MagicMock()
        connect_mock.return_value.__enter__.return_value = mock_connection

        expected_output = self.create_database_sql.replace(" ", "")

        with patch("sqlite3.connect", connect_mock):
            SQLiteHandler(self.database_path, self.table_name)
            received_output = mock_cursor.executescript.call_args[0][0]\
                .replace(" ", "")

        self.assertEqual(expected_output, received_output)
