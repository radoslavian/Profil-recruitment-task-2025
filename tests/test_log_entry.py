from unittest import TestCase
import datetime
from modules.log_entry import LogEntry


class RepresentationTestCase(TestCase):
    """
    Tests for LogEntry object's string representation.
    """
    @classmethod
    def setUpClass(cls):
        cls.date = datetime.datetime(1987, 3, 9, 11, 10, 10)
        cls.log_level = "WARNING"
        cls.message = "warning message"

        log_entry = LogEntry(date=cls.date,
                             log_level=cls.log_level,
                             message=cls.message)
        cls.received_output = repr(log_entry)

    def test_iso_date(self):
        """
        Representation should include iso-formatted date.
        """
        iso_date = self.date.isoformat()
        self.assertIn(iso_date, self.received_output)

    def test_log_level_name(self):
        """
        The representation should include a logging level.
        """
        self.assertIn(self.log_level, self.received_output)

    def test_message(self):
        """
        The representation should include a logged message.
        """
        self.assertIn(self.message, self.received_output)

    def test_output(self):
        """
        The representation output should be in the correct format.
        """
        expected_output = f"LogEntry(date={self.date.isoformat()}, "\
            f"log_level='{self.log_level}', message='{self.message}')"
        self.assertEqual(expected_output, self.received_output)
