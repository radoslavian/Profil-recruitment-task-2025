import datetime
from typing import List, Dict, Set, Optional
from modules.log_entry import LogEntry
from modules.handlers import Handler


class ProfilLoggerReader:
    def __init__(self, handler: Handler):
        self._handler = handler

    def find_by_text(
            self,
            text: str,
            start_date: Optional[datetime.datetime] = None,
            end_date: Optional[datetime.datetime] = None) -> List[LogEntry]:
        """
        Find log entries by a message text, optionally filtering
        them by dates.
        """
        filtered_entries = self._filter_all_logs_by_date(start_date, end_date)
        result_entries = self._filter_entries_by_text(filtered_entries, text)
        return result_entries

    @staticmethod
    def _filter_entries_by_text(logs, text):
        return [log for log in logs if text in log.message]

    def find_by_regex(
            self,
            regex: str,
            start_date: Optional[datetime.datetime] = None,
            end_date: Optional[datetime.datetime] = None) \
            -> List[LogEntry]:
        pass

    def groupby_level(
            self,
            start_date: Optional[datetime.datetime] = None,
            end_date: Optional[datetime.datetime] = None) \
            -> Dict[str, List[LogEntry]]:
        pass

    def groupby_month(
            self,
            start_date: Optional[datetime.datetime] = None,
            end_date: Optional[datetime.datetime] = None) \
            -> Dict[str, List[LogEntry]]:
        pass

    def _get_all_logs_from_handler(self) -> List[LogEntry]:
        return self._handler.retrieve_all_logs()

    def _filter_all_logs_by_date(
            self,
            start_date: Optional[datetime.datetime] = None,
            end_date: Optional[datetime.datetime] = None) -> List[LogEntry]:
        """
        Returns entries logged between start_date (the entry start_date is
        higher than) and end_date (the entry end_date is lower than).
        """
        all_entries: List = self._get_all_logs_from_handler()
        entries_from_start_date: Set = set()
        entries_before_end_date: Set = set()
        entries_union: List = []

        if start_date:
            entries_from_start_date = {entry for entry in all_entries
                                       if entry.date > start_date}

        if end_date:
            entries_before_end_date = {entry for entry in all_entries
                                       if entry.date < end_date}

        if start_date and end_date:
            entries_union_set = (entries_from_start_date
                                 & entries_before_end_date)
            entries_union = list(entries_union_set)

        return (entries_union
                or list(entries_from_start_date)
                or list(entries_before_end_date)
                or all_entries)
