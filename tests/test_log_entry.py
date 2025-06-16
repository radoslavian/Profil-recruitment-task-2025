from unittest import TestCase
import datetime
from modules.log_entry import LogEntry


# docstrings are ommited in cases where the test name
# is sufficiently descriptive


class LogEntryAttrEncapsulationConversion(TestCase):
    """
    Tests for attributes encapsulation and converting a LogEntry instance into:
    + a machine-readable string representation (obtained using repr())
    + Python dictionary
    """
    @classmethod
    def setUpClass(cls):
        cls.date = '1987-03-09T11:10:10'
        cls.log_level = "WARNING"
        cls.message = "warning message"

        cls.log_entry = LogEntry(date=cls.date,
                                 level=cls.log_level,
                                 msg=cls.message)

        cls.received_representation = repr(cls.log_entry)
        cls.received_dict = cls.log_entry.to_dict()

    def test_encapsulation_reading(self):
        self.assertEqual(self.log_entry.level, self.log_level)
        self.assertEqual(self.log_entry.date, self.date)
        self.assertEqual(self.log_entry.message, self.message)

    def test_encapsulation_writing(self):
        """
        Should fail on an attempt to overwrite a public attribute.
        """
        def fail_level():
            self.log_entry.level = "new level"

        def fail_date():
            self.log_entry.date = datetime.datetime(1988, 3, 9, 11, 10, 10)

        def fail_message():
            self.log_entry.message = "new message"

        self.assertRaises(AttributeError, fail_level)
        self.assertRaises(AttributeError, fail_date)
        self.assertRaises(AttributeError, fail_message)

    def test_iso_date(self):
        """
        Representation should include iso-formatted date.
        """
        self.assertIn(self.date, self.received_representation)

    def test_log_level_name(self):
        """
        The representation should include a logging level.
        """
        self.assertIn(self.log_level, self.received_representation)

    def test_message(self):
        """
        The representation should include a logged message.
        """
        self.assertIn(self.message, self.received_representation)

    def test_output(self):
        """
        The representation output should be in the correct format.
        """
        expected_output = f"LogEntry(date={self.date}, "\
            f"level='{self.log_level}', " \
            f"msg='{self.message}')"
        self.assertEqual(expected_output, self.received_representation)

    def test_dict_date(self):
        self.assertEqual(self.date, self.received_dict["date"])

    def test_dict_log_level(self):
        log_level_name = self.log_level
        self.assertEqual(log_level_name, self.received_dict["level"])

    def test_dict_message(self):
        self.assertEqual(self.message, self.received_dict["message"])
        

class LogEntryFromDict(TestCase):
    """
    Getting a new LogItem instance from a dictionary.
    """
    @classmethod
    def setUpClass(cls):
        cls.date = datetime.datetime(
            1987, 3, 9, 11, 10, 10)
        cls.log_entry = {"level": "ERROR",
                         "message": "logged message",
                         "date": cls.date.isoformat()}

        cls.log_entry_from_dict = LogEntry.from_dict(cls.log_entry)

    def test_log_level(self):
        self.assertEqual(self.log_entry_from_dict["level"],
                         self.log_entry["level"])

    def test_message(self):
        self.assertEqual(self.log_entry_from_dict["message"],
                         self.log_entry["message"])

    def test_date(self):
        self.assertEqual(self.log_entry_from_dict["date"],
                         self.date.isoformat())
