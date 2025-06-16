from unittest import TestCase
from unittest.mock import patch, mock_open
import datetime
from modules.handlers import FileHandler
from modules.log_entry import LogEntry, LogLevelValue
from .test_data import log_entry


@patch("builtins.open", new_callable=mock_open)
@patch("os.path.exists", return_value=False)
class FileAccessCreation(TestCase):
    """
    Tests for accessing/creating log csv files.
    """
    @classmethod
    def setUpClass(cls):
        cls.file_path = "/file/to/open.txt"

    def test_file_exists(self, mock_exists, _):
        """
        On receiving a filepath, __init__ should check if a file exists.
        """
        file_handler = FileHandler(self.file_path)
        mock_exists.assert_called_once_with(self.file_path)

    def test_opening_file(self, _, mock_open_file):
        """
        Should create an output file (if it doesn't exist).
        """
        FileHandler(self.file_path)
        mock_open_file.assert_called_once_with(self.file_path, "w")

    def test_writing_new_file(self, _, mock_file_open):
        FileHandler(self.file_path)
        handle = mock_file_open()
        handle.write.assert_called_once_with("")


class PersistingLogs(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.file_path = "/file/to/open.txt"
        cls.mock_file_open = mock_open()
        log_entry_d, cls.log_entry = log_entry()

    def setUp(self):
        with patch("builtins.open", self.mock_file_open):
            file_handler = FileHandler(self.file_path)
            file_handler.persist_log(self.log_entry)

    def test_file_opening(self):
        """
        The text file should be opened in a mode for adding new lines.
        """
        self.mock_file_open.assert_called_with(self.file_path, "a")

    def test_writing_log(self):
        """
        Should save a log entry into a file.
        """
        file_handle = self.mock_file_open()
        call_argument = (f"{self.log_entry.date} "
                         f"{self.log_entry.level} "
                         f"{self.log_entry.message}\n")
        file_handle.write.assert_called_with(call_argument)


class RetrieveLogs(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.log_entry_1 = {
            "date": "1987-03-09T11:10:10",  # isoformat date
            "level": "WARNING",
            "message": "1st logged message"}
        cls.log_entry_2 = {
            "date": "1987-03-10T11:10:10",
            "level": "ERROR",
            "message": "2nd logged message"}
        cls.read_data = (f"{cls.log_entry_1['date']} "
                         f"{cls.log_entry_1['level']} "
                         f"{cls.log_entry_1['message']}\n"
                         f"{cls.log_entry_2['date']} "
                         f"{cls.log_entry_2['level']} "
                         f"{cls.log_entry_2['message']}")
        cls.file_path = "/path/to/a/file.txt"
        cls.mock_file_open = mock_open(read_data=cls.read_data)

    def setUp(self):
        with patch("builtins.open", self.mock_file_open):
            file_handler = FileHandler(self.file_path)
            self.log_entries = file_handler.retrieve_all_logs()

    def test_opening_file(self):
        """
        Should open a file for reading.
        """
        self.mock_file_open.assert_called_with(self.file_path, "r")

    def test_fetching_entries(self):
        """
        Should load log entries from a file.
        """
        log_entry_1 = LogEntry.from_dict(self.log_entry_1).to_dict()
        log_entry_2 = LogEntry.from_dict(self.log_entry_2).to_dict()

        self.assertDictEqual(log_entry_1, self.log_entries[0].to_dict())
        self.assertDictEqual(log_entry_2, self.log_entries[1].to_dict())

    def test_malformed_input(self):
        """
        Should return empty list if the input file contains malformed data.
        """
        read_data = "malformed line" + self.read_data
        mock_file_open = mock_open(read_data=read_data)

        with patch("builtins.open", mock_file_open):
            file_handler = FileHandler(self.file_path)
            log_entries = file_handler.retrieve_all_logs()

        self.assertFalse(log_entries)
