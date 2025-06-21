import datetime
from typing import List, Dict, Set, Iterable, Optional
from modules.log_entry import LogEntry
from modules.handlers import Handler
from modules.log_entry import LogLevelValue
import re


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
            end_date: Optional[datetime.datetime] = None) -> List[LogEntry]:
        """
        Find log entries by a regular expression, optionally filtering
        them by dates.
        """
        filtered_entries = self._filter_all_logs_by_date(start_date, end_date)
        try:
            result_entries = self._filter_entries_by_regex(
                filtered_entries, regex)
        except re.error:
            return []

        return result_entries

    @staticmethod
    def _filter_entries_by_regex(entries, regex: str) -> List[LogEntry]:
        pattern = re.compile(regex)
        matching_logs = filter(
            lambda entry: pattern.search(entry.message), entries)

        return list(matching_logs)

    def groupby_level(
            self,
            start_date: Optional[datetime.datetime] = None,
            end_date: Optional[datetime.datetime] = None) \
            -> Dict[LogLevelValue, List[LogEntry]]:
        """
        Group log entries from an optionally given time period by
        logging levels.
        """
        log_entries = self._filter_all_logs_by_date(start_date, end_date)
        grouped_entries: Dict = {level: [entry for entry in log_entries
                                         if entry.level == level]
                                 for level in LogLevelValue}

        return {level: entries for level, entries
                in grouped_entries.items() if entries}

    def groupby_month(
            self,
            start_date: Optional[datetime.datetime] = None,
            end_date: Optional[datetime.datetime] = None) \
            -> Dict[str, List[LogEntry]]:
        """
        Group log entries in a dictionary by 'year-month' keys.
        """
        entries_filtered_by_date = self._filter_all_logs_by_date(
            start_date, end_date)
        year_month_keys = {entry.date.strftime("%Y-%m")
                           for entry in entries_filtered_by_date}
        entries_by_year_month = {
            year_month_key: [entry for entry
                             in entries_filtered_by_date
                             if entry.date.strftime("%Y-%m") == year_month_key]
            for year_month_key in year_month_keys
        }
        return entries_by_year_month

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
        entries_intersection: List = []

        if start_date:
            entries_from_start_date = {entry for entry in all_entries
                                       if entry.date > start_date}

        if end_date:
            entries_before_end_date = {entry for entry in all_entries
                                       if entry.date < end_date}

        if start_date and end_date:
            entries_intersection = self._sort_entries_by_date(
                entries_from_start_date
                & entries_before_end_date)

        if not any([entries_from_start_date, entries_before_end_date]) \
           and any([start_date, end_date]):
            all_entries = []

        return (entries_intersection
                or self._sort_entries_by_date(entries_from_start_date)
                or self._sort_entries_by_date(entries_before_end_date)
                or all_entries)

    @staticmethod
    def _sort_entries_by_date(entries: Iterable[LogEntry]) -> List[LogEntry]:
        return sorted(entries, key=lambda entry: entry.date)
