from unittest import TestCase
from unittest.mock import patch, mock_open
from modules.handlers import JsonHandler


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
