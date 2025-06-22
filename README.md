##### Radosław Kuzyk
## Requirements
The library was written and tested with Python 3.12.1.

## Tests
The unit tests were written using the PyUnit library. To run them, in the project directory
(i.e. the directory where this README.md file is located) execute the command:
```
[profil_recruitment_task_2025]$ python3 -m unittest discover
```

## Usage examples
### Loading into interpreter
The interpreter should be run in the `profil_recruitment_task_2025` directory:
```
[profil_recruitment_task_2025]$ python3
```
Then import all identifiers intended for an 'asterisk' import - *:
```
Python 3.12.1 (main, Jun 13 2025, 23:53:16) [GCC 7.5.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from profil_logger import *
>>>
```
### Logging
#### Creating handlers
In order to log events, you have to create an instance of one or more handlers:
~~~
>>> path_to_file = "/path/to/file_log.txt"
>>> file_handler = FileHandler(path_to_file_log)
>>>
~~~
Each handler supports absolute file paths.  
To create a handler for
a database, you must additionally provide the table name (the default is `log`):
~~~
>>> sqlite_handler = SQLiteHandler("/path/to/log.sqlite", table_name="my_log")
>>>
~~~
The handlers created in this way can be imported as a list to the ProfilLogger:
~~~
>>> logger = ProfilLogger([file_handler, sqlite_handler])
>>>
~~~
#### Logging entries
Logger does not log entries with a logging level lower than the currently set one.
The default level is DEBUG. The logging level can be changed using the method
`ProfilLogger.set_log_level()`, whose argument is an object of the
`Enum` type - `LogLevelValue`:
~~~
>>> logger.set_log_level(LogLevelValue.INFO)
>>>
~~~
Events are logged using methods whose names correspond to logging levels:
~~~
>>> logger.warning("something went not exactly as it should")
>>>
>>> logger.debug("debug message")
>>>
~~~
Entries logged in this way will appear - in this case -
in the file and database.  
File:
~~~
2025-06-22T19:20:14.521587 WARNING something went not exactly as it should
2025-06-22T19:24:12.445347 ERROR an error killed all good servers!
~~~
Database:
~~~
...
13|2025-06-22T19:11:56.904995|INFO|info message
14|2025-06-22T19:20:14.521587|WARNING|something went not exactly as it should
15|2025-06-22T19:24:12.445347|ERROR|an error killed all good servers!
~~~

## Reading the log
### Searching by text and regular expressions
LoggerReader class is used to read log entries, with handler as an argument:
~~~
>>> logger_reader = ProfilLoggerReader(sqlite_handler)
>>>
~~~
Entries can be searched by text in messages of the entries:
~~~
>>> logger_reader.find_by_text("something")
[LogEntry(date=2025-06-22T19:20:14.521587, level='WARNING', message='something went not exactly as it should')]
>>>
~~~
or using regular expressions:
~~~
>>> logger_reader.find_by_regex(r"^s.+g\s")
[LogEntry(date=2025-06-22T19:20:14.521587, level='WARNING', message='something went not exactly as it should')]
~~~
For both of the above methods, you can use optional boundary dates (between which
the entries were logged) - `datetime.datetime` objects.

### Grouping by date (year-month):
To group entries by logging levels, use the method:
~~~
>>> logger_reader.groupby_month()
~~~
The method returns a dictionary whose keys are the year-month strings: `'2025-06'` and the values are a list of LogEntry objects.
Such a structure can be converted to a dictionary serializable to json format - e.g. using the following expression:
~~~
>>> json.dumps({k: [val.to_dict() for val in v] for k, v in logger_reader.groupby_month().items()})
>>>
~~~
The output after reformatting can look like this:
```
{
  "2025-06": [
    {
      "date": "2025-06-22T13:36:12.774871",
      "level": "DEBUG",
      "message": "debug message"
    },
    {
      "date": "2025-06-22T13:36:12.851657",
      "level": "INFO",
      "message": "info message"
    },
   ...
  ]
 ...
}
```
### Grouping by logging levels
The following method is used to group by logging levels:
~~~
>>> logger_reader.groupby_level()
{<LogLevelValue.DEBUG: 0>: [LogEntry(date=2025-06-22T13:36:12.774871, level='DEBUG', message='debug message') ... ]}
~~~
In this case I chose the LogLevelValue object as the dictionary key: because it is hashable and contains more information
than a text string. Any conversion to a json object would require converting the list
of LogEntry objects anyways. To do that, you can use the expression:
```
>>> json.dumps({k.name: [val.to_dict() for val in v] for k, v in logger_reader.groupby_level().items()})
```
The formatted output would look like this:
```
{
  "DEBUG": [
    {
      "date": "2025-06-22T13:36:12.774871",
      "level": "DEBUG",
      "message": "debug message"
    },
    {
      "date": "2025-06-22T14:09:27.700686",
      "level": "DEBUG",
      "message": "debug message"
    }
  ],
  "INFO": [
    {
      "date": "2025-06-22T13:36:12.851657",
      "level": "INFO",
      "message": "info message"
    },
  ...
 ]
 ...
}
```
For both grouping methods, you can optionally use boundary dates in the `datetime` format.

## Notes:
* The methods for browsing/searching entries return entries whose date is _greater or equal_ to the start date and entries whose date is _less than or equal_ to the end date.
* I replaced the word 'msg' with 'message' in:
  + LogEntry
  + Log files and SQLite table
Please keep this in mind - if you have any test files that have 'msg' in the database table/CSV file header/as a json field - fetching data from there will fail.
