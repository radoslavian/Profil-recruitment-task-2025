from unittest import TestCase
import datetime
from modules.log_entry import LogEntry, LogLevelValue


# docstrings are ommited in cases where the test name
# is sufficiently descriptive

class LogEntryTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.date = datetime.datetime(1987, 3, 9, 11, 10, 10)
        cls.log_level_value = "WARNING"
        cls.log_level = LogLevelValue[cls.log_level_value]
        cls.message = "warning message"

        log_entry = LogEntry(date=cls.date,
                             log_level=cls.log_level,
                             message=cls.message)

        cls.received_representation = repr(log_entry)
        cls.received_dict = log_entry.to_dict()

    def test_iso_date(self):
        """
        Representation should include iso-formatted date.
        """
        iso_date = self.date.isoformat()
        self.assertIn(iso_date, self.received_representation)

    def test_log_level_name(self):
        """
        The representation should include a logging level.
        """
        self.assertIn(self.log_level.name, self.received_representation)

    def test_message(self):
        """
        The representation should include a logged message.
        """
        self.assertIn(self.message, self.received_representation)

    def test_output(self):
        """
        The representation output should be in the correct format.
        """
        expected_output = f"LogEntry(date={self.date.isoformat()}, "\
            f"level='{self.log_level_value}', " \
            f"msg='{self.message}')"
        self.assertEqual(expected_output, self.received_representation)

    def test_dict_date(self):
        iso_date = self.date.isoformat()
        self.assertEqual(iso_date, self.received_dict["date"])

    def test_dict_log_level(self):
        log_level_name = self.log_level.name
        self.assertEqual(log_level_name, self.received_dict["level"])

    def test_dict_message(self):
        self.assertEqual(self.message, self.received_dict["msg"])
