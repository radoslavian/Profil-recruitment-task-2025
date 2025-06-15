import datetime
from modules.log_entry import LogEntry, LogLevelValue


def log_entry():
    date = datetime.datetime(1987, 3, 9, 11, 10, 10)
    log_level_value = "WARNING"
    log_level = LogLevelValue[log_level_value]
    message = "logged message"
    log_entry_d = {"level": log_level,
                   "msg": message,
                   "date": date}
    log_entry = LogEntry.from_dict(log_entry_d)

    return log_entry_d, log_entry
