from unittest import TestCase
from unittest.mock import patch, mock_open
from modules.handlers import JsonHandler


class OpeningCreatingLog(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = "/path/to/file.json"

    @patch("builtins.open", new_callable=mock_open)
    def test_opening_file(self, mock_open_file):
        """
        Should check if the file exists and if doesn't - create one
        and open for writing.
        """
        with patch("os.path.exists", return_value=False) as mock_exists:
            JsonHandler(self.path)

        mock_exists.assert_called_once_with(self.path)
        mock_open_file.assert_called_once_with("/path/to/file.json", "w")

    def test_initializing_file(self):
        """
        Should save an empty json array to a newly created file.
        """
        mock_file_open = mock_open()
        with patch("builtins.open", mock_file_open):
            JsonHandler(self.path)
        handle = mock_file_open()
        handle.write.assert_called_once_with("[]")
