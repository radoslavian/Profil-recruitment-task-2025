from unittest import TestCase
from unittest.mock import patch, mock_open, MagicMock
import json
from modules.handlers import JsonHandler
from .test_data import log_entry


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


