from unittest import TestCase, skip
from unittest.mock import patch, MagicMock
import datetime
from modules.log_entry import LogEntry, LogLevelValue
from modules.handlers import FileHandler
from modules.profil_logger_reader import ProfilLoggerReader


class TestData:
    log_file_path = "/path/to/log/file.txt"
    entries = [
        # 0
        {
            'level': 'DEBUG',
            'message': 'DJs flock by when MTV ax quiz prog.',
            'date': '1994-10-02T07:38:07'
        },
        # 1
        {
            'level': 'CRITICAL',
            'message': 'Junk MTV quiz graced by fox whelps.',
            'date': '1996-12-28T03:32:42'
        },
        # 2
        {
            'level': 'DEBUG',
            'message': 'Bawds jog, flick quartz, vex nymphs.',
            'date': '2003-10-22T10:49:46'
        },
        # 3
        {
            'level': 'CRITICAL',
            'message': 'The quick, brown fox jumps over a lazy dog.',
            'date': '2013-12-10T09:37:54'
        },
        # 4
        {
            'level': 'ERROR',
            'message': 'How quickly daft jumping zebras vex.',
            'date': '2017-03-17T08:54:58'
        }
    ]
    log_entries = [LogEntry.from_dict(entry) for entry in entries]


# Testing regex search is similar to testing text search,
# so I moved the method for setting up data for the tests
# outside the test case class
# so that I could assign it to the setUp method in both
# classes - looks weird, but works.
# Another would be to create a generic class with
# the setUp for both classes, but this would require
# using multiple inheritance and writing more boiler plate code.

def setUpTestData(self, *args):
    self.mock_retrieve_all_logs = MagicMock(
        return_value=TestData.log_entries)
    self.handler = FileHandler(TestData.log_file_path)
    self.handler.retrieve_all_logs = self.mock_retrieve_all_logs
    self.logger_reader = ProfilLoggerReader(self.handler)


class TextSearch(TestCase):
    setUp = patch("builtins.open")(setUpTestData)

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
                            for entry in (TestData.log_entries[0],
                                          TestData.log_entries[1],)}

        self.mock_retrieve_all_logs.assert_called_once()
        self.assertEqual(expected_number_of_entries, len(found_entries))
        self.assertSetEqual(expected_entries, received_entries)

    def test_start_date_end_date(self):
        """
        It should search for entries by a text input and return entries
        logged between the start_date and the end_date.
        """
        searched_text = "vex"
        expected_number_of_entries = 1
        start_date = datetime.datetime.fromisoformat("1996-12-28T03:32:42")
        end_date = datetime.datetime.fromisoformat("2013-12-10T09:37:54")

        found_entries = self.logger_reader.find_by_text(
            searched_text, start_date=start_date, end_date=end_date)
        expected_entries = [TestData.log_entries[2]]

        self.mock_retrieve_all_logs.assert_called_once()
        self.assertEqual(expected_number_of_entries, len(found_entries))
        self.assertListEqual(expected_entries, found_entries)

    def test_start_date_only(self):
        """
        It should search for entries logged after the start_date.
        """
        searched_text = "MTV"
        start_date = datetime.datetime.fromisoformat("1994-11-02T07:38:07")
        found_entries = self.logger_reader.find_by_text(
            searched_text, start_date=start_date)
        expected_entries = [TestData.log_entries[1]]

        self.assertListEqual(expected_entries, found_entries)

    @skip("Will be written after the tested class is completed.")
    def test_end_date_only(self):
        """
        It should search for entries logged before the end_date.
        """
        pass


class RegexSearch(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.searched_expression = r"\,\s\w{5}\s"  # should capture 2 and 3
        cls.start_date = datetime.datetime.fromisoformat('2003-10-22T10:49:46')
        cls.end_date = datetime.datetime.fromisoformat('2017-03-17T08:54:58')

    setUp = patch("builtins.open")(setUpTestData)

    def test_calling_handler(self):
        """
        It should call the handler.retrieve_all_logs() method.
        """
        self.logger_reader.find_by_regex(self.searched_expression)
        self.mock_retrieve_all_logs.assert_called_once()

    def test_no_dates(self):
        """
        It should search for entries by a regular expression input without
        filtering by dates.
        """
        found_entries = self.logger_reader.find_by_regex(
            self.searched_expression)
        expected_number_of_entries = 2
        received_entries = {repr(entry) for entry in found_entries}
        expected_entries = {repr(entry)
                            for entry in (TestData.log_entries[2],
                                          TestData.log_entries[3],)}

        self.assertEqual(expected_number_of_entries, len(found_entries))
        self.assertSetEqual(expected_entries, received_entries)

    def test_start_date_end_date(self):
        found_entries = self.logger_reader.find_by_regex(
            self.searched_expression, self.start_date, self.end_date)
        expected_number_of_entries = 1
        received_entry = repr(found_entries[0])
        expected_entry = repr(TestData.log_entries[3])

        self.assertEqual(expected_number_of_entries, len(found_entries))
        self.assertEqual(expected_entry, received_entry)

    def test_exception(self):
        """
        It should handle re.error exception and return an empty
        list of entries.
        """
        invalid_pattern = r"[]"
        found_entries = self.logger_reader.find_by_regex(invalid_pattern)

        self.assertFalse(found_entries)

    @skip("Will be written after the tested class is completed.")
    def test_start_date_only(self):
        """
        It should search for entries logged after the start_date.
        """
        pass

    @skip("Will be written after the tested class is completed.")
    def test_end_date_only(self):
        """
        It should search for entries logged after the end_date.
        """
        pass


class GroupingByLevel(TestCase):
    setUp = patch("builtins.open")(setUpTestData)

    def test_calling_handler(self):
        """
        It should call a handler to obtain log entries.
        """
        self.logger_reader.groupby_level()
        self.mock_retrieve_all_logs.assert_called_once()

    def test_no_dates(self):
        """
        It should group all log entries by levels, without filtering them
        by dates.
        """
        expected_output = {
            LogLevelValue.DEBUG: [TestData.log_entries[0],
                                  TestData.log_entries[2]],
            LogLevelValue.CRITICAL: [TestData.log_entries[1],
                                     TestData.log_entries[3]],
            LogLevelValue.ERROR: [TestData.log_entries[4]]
        }
        received_output = self.logger_reader.groupby_level()

        self.assertDictEqual(expected_output, received_output)

    @skip("As the functionality already exists, will be written after"
          " validating the library manually.")
    def test_start_date_end_date(self):
        """
        It should group log entries from a given time period by logging levels.
        """
        pass

    @skip("As the functionality already exists, will be written after"
          " validating the library manually.")
    def test_start_date_only(self):
        pass

    @skip("As the functionality already exists, will be written after"
          " validating the library manually.")
    def test_end_date_only(self):
        pass


class GroupingByMonth(TestCase):
    @classmethod
    def setUpClass(cls):
        entry = {
            'level': 'INFO',
            'message': 'Compilation finished at.',
            'date': '1996-12-21T04:31:27'
        }
        cls.entries = [*TestData.entries[:2], entry]
        cls.log_entries = [LogEntry.from_dict(entry) for entry in cls.entries]

    @patch("builtins.open")
    def setUp(self, *args):
        self.mock_retrieve_all_logs = MagicMock(
            return_value=self.log_entries)
        self.handler = FileHandler(TestData.log_file_path)
        self.handler.retrieve_all_logs = self.mock_retrieve_all_logs
        self.logger_reader = ProfilLoggerReader(self.handler)

    def test_calling_handler(self):
        """
        It should call a handler to obtain log entries.
        """
        self.logger_reader.groupby_month()
        self.mock_retrieve_all_logs.assert_called_once()

    def test_no_dates(self):
        """
        It should group all entries by year-month without filtering them by
        boundary dates.
        """
        expected_output = {
            "1994-10": [self.log_entries[0]],
            "1996-12": self.log_entries[1:]
        }
        received_output = self.logger_reader.groupby_month()

        self.assertDictEqual(expected_output, received_output)
