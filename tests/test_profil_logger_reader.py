from unittest import TestCase
from unittest.mock import patch, MagicMock
import datetime
from modules.log_entry import LogEntry
from modules.handlers import FileHandler
from modules.profil_logger_reader import ProfilLoggerReader


class TextSearch(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.log_file_path = "/path/to/log/file.txt"
        entries = [
            {
                'level': 'DEBUG',
                'message': 'DJs flock by when MTV ax quiz prog.',
                'date': '1994-10-02T07:38:07'
            },
            {
                'level': 'CRITICAL',
                'message': 'Junk MTV quiz graced by fox whelps.',
                'date': '1996-12-28T03:32:42'
            },
            {
                'level': 'DEBUG',
                'message': 'Bawds jog, flick quartz, vex nymphs.',
                'date': '2003-10-22T10:49:46'
            },
            {
                'level': 'CRITICAL',
                'message': 'The quick, brown fox jumps over a lazy dog.',
                'date': '2013-12-10T09:37:54'
            },
            {
                'level': 'ERROR',
                'message': 'How quickly daft jumping zebras vex.',
                'date': '2017-03-17T08:54:58'
            }
        ]
        cls.log_entries = [LogEntry.from_dict(entry) for entry in entries]

    @patch("builtins.open")
    def setUp(self, *args):
        self.mock_retrieve_all_logs = MagicMock(return_value=self.log_entries)
        self.handler = FileHandler(self.log_file_path)
        self.handler.retrieve_all_logs = self.mock_retrieve_all_logs
        self.logger_reader = ProfilLoggerReader(self.handler)

    def test_no_dates(self):
        """
        It should search for entries by a text input without filtering
        by dates.
        """
        searched_text = "MTV"
        found_entries = self.logger_reader.find_by_text(searched_text)

        expected_number_of_entries = 2
        received_entries = {repr(entry) for entry in found_entries}
        expected_entries = {repr(entry)
                            for entry in (self.log_entries[0],
                                          self.log_entries[1],)}

        self.mock_retrieve_all_logs.assert_called_once()
        self.assertEqual(expected_number_of_entries, len(found_entries))
        self.assertSetEqual(expected_entries, received_entries)

    def test_start_date_end_date(self):
        """
        It should search for entries by a text input and return entries
        logged between the start_date and the end_date.
        """
        start_date = datetime.datetime.fromisoformat("1996-12-28T03:32:42")
        end_date = datetime.datetime.fromisoformat("2013-12-10T09:37:54")
        searched_text = "vex"

        found_entries = self.logger_reader.find_by_text(
            searched_text, start_date=start_date, end_date=end_date)

        expected_number_of_entries = 1
        received_entries = {repr(entry) for entry in found_entries}
        expected_entries = {repr(self.log_entries[2])}

        self.mock_retrieve_all_logs.assert_called_once()
        self.assertEqual(expected_number_of_entries, len(found_entries))
        self.assertSetEqual(expected_entries, received_entries)
