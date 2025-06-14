from unittest import TestCase
from unittest.mock import patch, mock_open, MagicMock
from modules.handlers import FileHandler


@patch("builtins.open", new_callable=mock_open)
@patch("os.path.exists", return_value=False)
class FileHandlerFileAccessCreation(TestCase):
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
        with patch('builtins.open', m):
            FileHandler(self.file_path)
        handle = m()
        handle.write.assert_called_once_with("")


class FileHandlerPersistingLogs(TestCase):
    pass
