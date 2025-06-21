from unittest import TestCase
from unittest.mock import patch, mock_open, MagicMock
from .fake_data import fake_log_entry
from modules.handlers import CSVHandler


@patch("builtins.open", new_callable=mock_open)
class LogFileAccessCreation(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.filepath = "/path/to/file.csv"

    def setUp(self):
        self.writer_mock = MagicMock()
        self.writer_mock.return_value.writerow = MagicMock()

    @patch("os.path.exists", return_value=False)
    def test_no_log_file(self, *args):
        """
        It should create a new log file if it doesn't exist and write
        a header into it.
        """
        self.assert_log_created_header_written(args[-1])

    @patch("os.path.exists", return_value=True)
    @patch("os.path.getsize", return_value=0)
    def test_empty_log_file(self, *args):
        """
        It should write a header into an empty log file.
        """
        self.assert_log_created_header_written(args[-1])

    @patch("os.path.exists", return_value=True)
    @patch("os.path.getsize", return_value=1)
    def test_non_empty_file_exists(self, *args):
        """
        It should do nothing if the log file is non-empty.
        """
        def raise_assertion_error():
            self.assert_log_created_header_written(args[-1])

        self.assertRaises(AssertionError, raise_assertion_error)

    def assert_log_created_header_written(self, mock_open_file):
        file_handle = mock_open_file()

        with patch("csv.writer", new=self.writer_mock):
            CSVHandler(self.filepath)

        mock_open_file.assert_any_call(self.filepath, 'w', newline='')
        self.writer_mock.assert_any_call(file_handle)
        self.writer_mock.return_value.writerow.assert_called_once_with(
            ["date", "level", "message"])


class PersistingLogs(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.file_path = "/path/to/file.csv"
        _, cls.log_entry = fake_log_entry()

    def setUp(self):
        self.writer_mock = MagicMock()
        self.writer_mock.return_value.writerow = MagicMock()

    @patch("builtins.open", new_callable=mock_open)
    def test_persisting_log_entry(self, mock_open_file):
        file_handle = mock_open_file()

        with patch("csv.writer", new=self.writer_mock):
            cvs_handler = CSVHandler(self.file_path)
            cvs_handler.persist_log(self.log_entry)

        mock_open_file.assert_any_call(self.file_path, "a", newline="")
        self.writer_mock.assert_any_call(file_handle)
        self.writer_mock.return_value.writerow.assert_any_call([
            self.log_entry["date"],
            self.log_entry["level"],
            self.log_entry["message"]])


@patch("builtins.open", new_callable=mock_open)
class LogRetrieval(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.file_path = "/path/to/file.cls"

        number_of_entries = range(0, 2)
        log_entries = [fake_log_entry() for i in number_of_entries]

        # dictionaries from which fake entries had been created:
        cls.log_entries_data = [log_entry[0] for log_entry in log_entries]

        # actual fake LogEntry instances:
        cls.log_entries = [log_entry[1] for log_entry in log_entries]

    def setUp(self):
        with patch("builtins.open", new_callable=mock_open):
            self.csv_handler = CSVHandler(self.file_path)

    def test_log_file_opening(self, open_file):
        """
        It should successfully open a log file for reading.
        """
        self.csv_handler.retrieve_all_logs()
        open_file.assert_any_call(self.file_path, "r", newline="")

    def test_reading_log(self, open_file):
        """
        It should successfully read log data from a log file.
        """
        # csv.DictReader - returns a generator object
        # for reading log data sequentially
        # (mocking the generator with a list of dictionaries should suffice).

        file_handle = open_file()
        with patch("csv.DictReader",
                   return_value=self.log_entries_data) as mock_reader:
            log_entries = self.csv_handler.retrieve_all_logs()

        # comparing lists of string representations of LogEntry objects
        expected_entries = [repr(entry) for entry in self.log_entries]
        received_entries = [repr(entry) for entry in log_entries]

        mock_reader.assert_any_call(file_handle)
        self.assertListEqual(expected_entries, received_entries)

    def test_file_not_found(self, *args):
        """
        It should return an empty list in case of failure to open the file.
        """
        # mocked 'open' callable should raise the FileNotFoundError
        def fail_with_file_not_found(*args, **kwargs):
            raise FileNotFoundError

        with patch("builtins.open", new=fail_with_file_not_found):
            log_entries = self.csv_handler.retrieve_all_logs()

        self.assertFalse(log_entries)

