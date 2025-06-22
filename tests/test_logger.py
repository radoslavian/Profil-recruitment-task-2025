import datetime
from typing import Callable
from unittest import TestCase
from unittest.mock import MagicMock, patch
from profil_logger import FileHandler, JsonHandler, LogEntry, logger, \
    LogLevelValue, ProfilLogger


@patch("builtins.open")
@patch(f"{logger.__name__}.datetime", wraps=datetime)
class LoggingMessages(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.json_file_path = "/path/to/file.json"
        cls.file_path = "/path/to/file.txt"

        # mock datetime.datetime.now() with this:
        cls.logging_date = datetime.datetime(2021, 1, 12, 10, 15, 20, 2332)
        cls.logged_message = "logged message"
        cls.log_level = LogLevelValue["WARNING"]
        cls.entry = LogEntry(date=cls.logging_date,
                             level=cls.log_level,
                             msg=cls.logged_message)

    @patch("builtins.open")
    def setUp(self, *args):
        self.mock_file_persist_log = MagicMock()
        self.mock_json_persist_log = MagicMock()

        handlers = [FileHandler(self.file_path),
                    JsonHandler(self.json_file_path)]

        self.profil_logger = ProfilLogger(handlers)

    def test_default_log_level(self, mock_datetime: datetime.datetime, *args):
        """
        It should send a message with a log level higher (than the default
        one set on the object) to the file handlers.
        """
        mock_datetime.datetime.now.return_value = self.logging_date

        self._patch_handlers(
            lambda: self.profil_logger.warning(message=self.logged_message))

        expected_call = repr(self.entry)
        received_call_file_handler = repr(
            self.mock_file_persist_log.call_args[0][0])
        received_call_json_handler = repr(
            self.mock_json_persist_log.call_args[0][0])

        self.assertEqual(expected_call, received_call_file_handler)
        self.assertEqual(expected_call, received_call_json_handler)

    def test_lower_log_level(self, mock_datetime: datetime.datetime, *args):
        """
        It shouldn't log a message with a log_level lower than set on
        the ProfilLogger instance.
        """
        mock_datetime.datetime.now.return_value = self.logging_date
        log_level_critical = LogLevelValue["CRITICAL"]
        self.profil_logger.set_log_level(log_level_critical)
        self._patch_handlers(
            lambda: self.profil_logger.warning(message=self.logged_message))

        self.mock_file_persist_log.assert_not_called()
        self.mock_json_persist_log.assert_not_called()

    def test_equal_log_level(self, mock_datetime: datetime.datetime, *args):
        """
        It should log a message with a log_level equal to the one set on the
        ProfilLogger instance.
        """
        mock_datetime.datetime.now.return_value = self.logging_date
        log_level_critical = LogLevelValue["CRITICAL"]
        self.profil_logger.set_log_level(log_level_critical)
        self._patch_handlers(
            lambda: self.profil_logger.critical(message=self.logged_message))

        self.mock_file_persist_log.assert_called()
        self.mock_json_persist_log.assert_called()

    def test_debug_logging(self, mock_datetime: datetime.datetime, *args):
        """
        It should log a debug message.
        """
        mock_datetime.datetime.now.return_value = self.logging_date
        log_level_debug = LogLevelValue["DEBUG"]
        self.profil_logger.set_log_level(log_level_debug)
        self._patch_handlers(
            lambda: self.profil_logger.debug(message=self.logged_message))

        self.mock_file_persist_log.assert_called()

    def test_info_logging(self, mock_datetime: datetime.datetime, *args):
        """
        It should log an info message.
        """
        mock_datetime.datetime.now.return_value = self.logging_date
        log_level_info = LogLevelValue["INFO"]
        self.profil_logger.set_log_level(log_level_info)
        self._patch_handlers(
            lambda: self.profil_logger.info(message=self.logged_message))

        self.mock_file_persist_log.assert_called()

    def test_error_logging(self, mock_datetime: datetime.datetime, *args):
        """
        It should log an error message.
        """
        mock_datetime.datetime.now.return_value = self.logging_date
        log_level_error = LogLevelValue["ERROR"]
        self.profil_logger.set_log_level(log_level_error)
        self._patch_handlers(
            lambda: self.profil_logger.error(message=self.logged_message))

        self.mock_file_persist_log.assert_called()

    def _patch_handlers(self, _callable: Callable):
        with patch.object(FileHandler, "persist_log",
                          self.mock_file_persist_log):
            with patch.object(JsonHandler, "persist_log",
                              self.mock_json_persist_log):
                _callable()
