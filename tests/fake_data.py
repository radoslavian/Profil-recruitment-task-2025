import datetime
from modules.log_entry import LogEntry
import random as rnd


def rand_year():
    return rnd.randint(1955, 2020)


def rand_day():
    return rnd.randint(1, 28)


def rand_month_hour():
    return rnd.randint(1, 12)


def rand_min_sec():
    return rnd.randint(1, 59)


def rand_isoformat_date():
    """
    Returns string ISO 8601 date representation.
    """
    return datetime.datetime(
        rand_year(),
        rand_month_hour(),
        rand_day(),
        rand_month_hour(),
        rand_min_sec(),  # minute
        rand_min_sec(),  # second
    ).isoformat()


def rand_log_level_value():
    log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    return rnd.choice(log_levels)


def rand_message():
    messages = ["message 1", "message 2", "message 3", "message 4"]
    return rnd.choice(messages)


def fake_log_entry():
    log_entry_d = {"level": rand_log_level_value(),
                   "message": rand_message(),
                   "date": rand_isoformat_date()}
    log_entry = LogEntry.from_dict(log_entry_d)
    return log_entry_d, log_entry


def log_entry():
    date = datetime.datetime(1987, 3, 9, 11, 10, 10).isoformat()
    log_level = "WARNING"
    message = "logged message"
    log_entry_d = {"level": log_level,
                   "message": message,
                   "date": date}
    log_entry = LogEntry.from_dict(log_entry_d)

    return log_entry_d, log_entry
