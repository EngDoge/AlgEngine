import os
import sys
import logging
import traceback
import functools

from enum import Enum, auto
from logging import Formatter
from logging.handlers import RotatingFileHandler


from .logger import get_logger, simple_log_format, rotator, namer


DEBUG_LOG_FILE = "/tmp/algengine.log"


class FormatInfoEnum(Enum):
    def __str__(self):
        return f"{self.__class__.__name__}[{self.name}]"

    def __repr__(self):
        return f"{self.__class__.__name__}[{self.name}]"
    
class Status(FormatInfoEnum):
    OK = auto()
    Unknown = auto()
    Cancelled = auto()
    InvalidArgument = auto()
    DeadlineExceeded = auto()
    NotFound = auto()
    AlreadyExists = auto()
    PermissionDenied = auto()
    ResourceExhausted = auto()
    FailedPrecondition = auto()
    Aborted = auto()
    OutOfRange = auto()
    NotImplemented = auto()
    Internal = auto()
    Unavailable = auto()
    DataLoss = auto()
    Unauthenticated = auto()
    
class Supervisor:
    def __init__(self,
                 log_by_pid=True,
                 log_file=None,
                 file_mode='w',
                 log_level="INFO",
                 detail_log=False,
                 debug_mode=False):

        self.log_by_pid = log_by_pid
        self.log_file = log_file
        self.file_mode = file_mode
        self.debug_mode = debug_mode
        self.detail_log = detail_log
        self.log_level = self.get_log_level(log_level) if isinstance(log_level, str) else log_level
        self._is_bind_debug_log = False

    @property
    def logger(self):
        name = str(os.getpid()) if self.log_by_pid else 'supervisor'
        return get_logger(name=name, log_level=self.log_level, log_file=self.log_file)

    @staticmethod
    def format_tb(exc_traceback, limit=None):
        return ''.join(traceback.format_tb(exc_traceback, limit=limit))

    @property
    def info(self):
        return self.logger.info

    @property
    def debug(self):
        return self.logger.debug

    @property
    def warning(self):
        return self.logger.warning

    @property
    def error(self):
        return self.logger.error

    @property
    def critical(self):
        return self.logger.critical

    @property
    def log(self):
        return self.logger.log

    @staticmethod
    def get_log_level(level: str):
        return getattr(logging, level.upper())

    def set(self, log_file=None, file_mode='w', log_level="INFO"):
        self.log_file = log_file
        self.file_mode = file_mode
        self.log_level = self.get_log_level(log_level) if isinstance(log_level, str) else log_level

    def enable_debug(self):
        self.debug_mode = True

    def disable_debug(self):
        self.debug_mode = False

    def enable_detail_log(self):
        self.detail_log = True

    def disable_detail_log(self):
        self.detail_log = False

    def bind_debug_log_file(self, log_file=DEBUG_LOG_FILE):
        if not self._is_bind_debug_log:
            log_file = os.path.expanduser(log_file)
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            handler = RotatingFileHandler(log_file, maxBytes=500000000, backupCount=10, encoding="utf-8")
            handler.rotator = rotator
            handler.namer = namer
            handler.setLevel(logging.DEBUG)
            handler.setFormatter(Formatter(simple_log_format))
            self.logger.addHandler(handler)
            self._is_bind_debug_log = True

    def catch_error(self, e, limit=None):
        if self.debug_mode:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            formatted_traceback = self.format_tb(exc_traceback, limit=limit)
            s = type(exc_value).__name__ + ": " + str(exc_value)
            msg = '\n' + formatted_traceback + s
        else:
            msg = e
        self.error(msg)


    def watch(self, func, limit=None):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except TypeError as e:
                self.catch_error(e, limit=limit)
                status = Status.InvalidArgument
            except ValueError as e:
                self.catch_error(e, limit=limit)
                status = Status.InvalidArgument
            except NotImplementedError as e:
                self.catch_error(e, limit=limit)
                status = Status.NotImplemented
            except RuntimeError as e:
                self.catch_error(e, limit=limit)
                status = Status.DeadlineExceeded
            except IndexError as e:
                self.catch_error(e, limit=limit)
                status = Status.OutOfRange
            except KeyError as e:
                self.catch_error(e, limit=limit)
                status = Status.NotFound
            except Exception as e:
                self.catch_error(e, limit=limit)
                status = Status.Unknown
            else:
                status = Status.OK

            return status

        return wrapper

    def _sustain(self, func, default=None, limit=None):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self.catch_error(e, limit=limit)
                return default

        return wrapper

    def sustain(self, func=None, default=None, limit=None):
        if func is None:
            return functools.partial(self._sustain, default=default)
        return self._sustain(func, default=default, limit=limit)


supervisor = Supervisor(debug_mode=True)
