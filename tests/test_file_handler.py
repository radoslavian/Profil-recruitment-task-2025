from unittest import TestCase
from unittest.mock import patch, mock_open
import datetime
from modules.handlers import FileHandler
from modules.log_entry import LogEntry, LogLevelValue


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

    def test_writing_new_file(self, *rest):
        # TODO: how to get the same result using patch as a decorator?
        m = mock_open()
        with patch("builtins.open", m):
            FileHandler(self.file_path)
        handle = m()
        handle.write.assert_called_once_with("")


class PersistingLogs(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.file_path = "/file/to/open.txt"
        cls.mock_file_open = mock_open()
        date = datetime.datetime(1987, 3, 9, 11, 10, 10)
        log_level_value = "WARNING"
        log_level = LogLevelValue[log_level_value]
        message = "logged message"
        log_entry_d = {"level": log_level,
                       "msg": message,
                       "date": date}
        cls.log_entry = LogEntry.from_dict(log_entry_d)

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
        Should save log entry into a file.
        """
        file_handle = self.mock_file_open()
        call_argument = (f"{self.log_entry.date.isoformat()} "
                         f"{self.log_entry.level} "
                         f"{self.log_entry.message}\n")
        file_handle.write.assert_called_with(call_argument)
