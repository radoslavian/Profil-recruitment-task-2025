import json
from unittest import TestCase
from unittest.mock import MagicMock, mock_open, patch
from .fake_data import fake_log_entry, log_entry
from profil_logger import JsonHandler


@patch("builtins.open", new_callable=mock_open)
class OpeningCreatingLog(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = "/path/to/file.json"

    def test_creating_file(self, mock_open_file):
        """
        Should check if the file exists and if doesn't - create one
        and open it for writing.
        """
        with patch("os.path.exists", return_value=False) as mock_exists:
            JsonHandler(self.path)

        mock_exists.assert_called_once_with(self.path)
        mock_open_file.assert_called_once_with("/path/to/file.json", "w")

    @patch("os.path.exists", return_value=True)
    def test_opening_file(self, mock_exists, mock_open_file):
        """
        Shouldn't open an existing output file.
        """
        mock_file_open = mock_open_file()
        JsonHandler(self.path)
        mock_file_open.write.assert_not_called()

    def test_initializing_file(self, mock_open_file):
        """
        Should save an empty json array to a newly created file.
        """
        handle = mock_open_file()

        JsonHandler(self.path)
        handle.write.assert_called_once_with("[]")


class LogPersistance(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.log_entry_d, cls.log_entry = log_entry()
        cls.path = "/path/to/file.json"

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists", return_value=True)
    @patch("os.path.getsize", return_value=1)
    @patch("json.dump")
    def test_loading_data(self, mock_json_dump, mock_getsize, mock_exists,
                          mock_file_open):
        """
        Should load json data from a file for appending new entries.
        """
        with patch("json.load", new_callable=MagicMock()) as mock_json_load:
            with mock_file_open() as file_handle:
                json_handler = JsonHandler(self.path)
                json_handler.persist_log(self.log_entry)
                mock_json_load.assert_called_once_with(file_handle)
        mock_file_open.assert_any_call(self.path, "r")

    @patch("builtins.open")
    @patch("os.path.exists", return_value=False)
    @patch("os.path.getsize", return_value=1)
    def test_saving_data(self, mock_getsize, mock_exists, mock_file_open):
        json_handler = JsonHandler(self.path)
        with patch("json.dump", new_callable=MagicMock()) as mock_json_dump:
            json_handler.persist_log(self.log_entry)
            with mock_file_open() as file_handle:
                mock_json_dump.assert_called_once_with(
                    [self.log_entry.to_dict()], file_handle, indent=4)


@patch("builtins.open", new_callable=mock_open)
class LogsRetrieval(TestCase):
    """
    Test suite for the JsonHandler.retrieve_all_logs() method.
    """
    @classmethod
    def setUpClass(cls):
        cls.file_path = "/path/to/file.json"
        number_of_entries = range(0, 2)

        cls.log_entries = [fake_log_entry()[1] for i in number_of_entries]
        cls.log_entries_d = [log_entry.to_dict()
                             for log_entry in cls.log_entries]

    def test_file_opening(self, mock_file_open):
        """
        Should call 'open' to access the file.
        """
        with patch("json.load", return_value=self.log_entries_d):
            json_handler = JsonHandler(self.file_path)
            json_handler.retrieve_all_logs()
            mock_file_open.assert_any_call(self.file_path, "r")

    def test_json_data_loading(self, *args):
        with patch("json.load", return_value=self.log_entries_d):
            json_handler = JsonHandler(self.file_path)
            received_log_entries = set(
                str(log) for log in json_handler.retrieve_all_logs())
        expected_log_entries = set(str(log) for log in self.log_entries)

        self.assertSetEqual(expected_log_entries, received_log_entries)

    def test_file_not_found_exception(self, *args):
        """
        Should return empty list if FileNotFoundError occurs.
        """
        def raise_file_not_found_error(arg):
            raise FileNotFoundError

        with patch("json.load", new=raise_file_not_found_error):
            json_handler = JsonHandler(self.file_path)
            entries = json_handler.retrieve_all_logs()

        self.assertFalse(entries)

    def test_json_decoder_error_exception(self, *args):
        """
        Should return empty list if JSONDecodeError occurs.
        """
        def raise_json_decoder_error(arg):
            raise json.JSONDecodeError(
                "intentional exception", "doc", 1)

        with patch("json.load", new=raise_json_decoder_error):
            json_handler = JsonHandler(self.file_path)
            entries = json_handler.retrieve_all_logs()

        self.assertFalse(entries)
