from dataclasses import dataclass
from typing import Any
from colorama import Fore, Style, init
from collections.abc import Sequence

from .debug import debug_manager as manager

try:
    from numpy import bool_
except ImportError:
    bool_ = bool

init(autoreset=True)

DEBUG_MODE = False


@dataclass
class Params:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@dataclass
class LogParam:
    param: Any
    name: str
    __slots__ = ['param', 'name']

    def __init__(self, **kwargs):
        assert (num_kwargs := len(kwargs) == 1), f'Only one parameter is allowed, {num_kwargs} is given!'
        self.param = next(iter(kwargs.values()))
        self.name = next(iter(kwargs.keys()))

    @classmethod
    def set(cls, name: str, param: Any):
        return cls(**{name: param})

    def format_operation_log(self, other: Any, operation: str):
        if manager.color_mode:
            return f"{self} {Fore.RED}{operation}{Fore.RESET} {other}"
        return f"{self} {operation} {other}"

    def contains(self, item: Any, contains_all: bool = True):
        item_ = item.param if isinstance(item, LogParam) else item
        if isinstance(item_, str):
            flag = item_ in self.param
            is_seq = False
        elif is_seq := isinstance(item_, Sequence):
            eval_iterable = all if contains_all else any
            flag = eval_iterable(it_ in self.param for it_ in item_)
        else:
            flag = item_ in self.param
        if manager.debug_mode:
            operation = f'contains({"all" if contains_all else "any"})' if is_seq else 'contains'
            return LogParam.set(name=self.format_operation_log(other=item, operation=operation),
                                param=bool(flag))
        return flag

    def not_contain(self, item: Any, not_contain_any: bool = True):
        item_ = item.param if isinstance(item, LogParam) else item
        if isinstance(item_, str):
            flag = item_ not in self.param
            is_seq = False
        elif is_seq := isinstance(item_, Sequence):
            eval_iterable = any if not_contain_any else any
            flag = eval_iterable(it_ not in self.param for it_ in item_)
        else:
            flag = item_ not in self.param

        if manager.debug_mode:
            operation = f'not contain({"any" if not_contain_any else "all"})' if is_seq else 'not contain'
            return LogParam.set(name=self.format_operation_log(other=item, operation=operation),
                                param=bool(flag))
        return flag

    def __le__(self, other):
        if manager.debug_mode:
            return LogParam.set(name=self.format_operation_log(other=other, operation='<='),
                                param=bool(self.param <= (other.param if isinstance(other, LogParam)
                                                          else other)))
        return self.param <= (other.param if isinstance(other, LogParam) else other)

    def __lt__(self, other):
        if manager.debug_mode:
            return LogParam.set(name=self.format_operation_log(other=other, operation='<'),
                                param=bool(self.param < (other.param if isinstance(other, LogParam)
                                                         else other)))
        return self.param < (other.param if isinstance(other, LogParam) else other)

    def __ge__(self, other):
        if manager.debug_mode:
            return LogParam.set(name=self.format_operation_log(other=other, operation='>='),
                                param=bool(self.param >= (other.param if isinstance(other, LogParam)
                                                          else other)))
        return self.param >= (other.param if isinstance(other, LogParam) else other)

    def __gt__(self, other):
        if manager.debug_mode:
            return LogParam.set(name=self.format_operation_log(other=other, operation='>'),
                                param=bool(self.param > (other.param if isinstance(other, LogParam)
                                                         else other)))
        return self.param > (other.param if isinstance(other, LogParam) else other)

    def __eq__(self, other):
        if manager.debug_mode:
            return LogParam.set(name=self.format_operation_log(other=other, operation='=='),
                                param=bool(self.param == (other.param if isinstance(other, LogParam)
                                                          else other)))
        return self.param == (other.param if isinstance(other, LogParam) else other)

    def __ne__(self, other):
        if manager.debug_mode:
            return LogParam.set(name=self.format_operation_log(other=other, operation='!='),
                                param=bool(self.param != (other.param if isinstance(other, LogParam)
                                                          else other)))
        return self.param != (other.param if isinstance(other, LogParam) else other)

    def __or__(self, other):
        if manager.debug_mode:
            return LogParam.set(name=self.format_operation_log(other=other, operation='or'),
                                param=bool(self.param or (other.param if isinstance(other, LogParam)
                                                          else other)))
        return self.param or (other.param if isinstance(other, LogParam) else other)

    def __and__(self, other):
        if manager.debug_mode:
            return LogParam.set(name=self.format_operation_log(other=other, operation='and'),
                                param=self.param and (other.param if isinstance(other, LogParam)
                                                      else other))
        return self.param and (other.param if isinstance(other, LogParam) else other)

    def __contains__(self, item):
        if manager.debug_mode:
            return LogParam.set(name=self.format_operation_log(other=item, operation='in'),
                                param=bool((item.param if isinstance(item, LogParam) else item) in self.param))
        return (item.param if isinstance(item, LogParam) else item) in self.param

    def __bool__(self):
        return bool(self.param)

    def __repr__(self):
        return str(self)

    def __str__(self):
        if manager.color_mode:
            param_color = (Fore.GREEN if self.param else Fore.RED) if isinstance(self.param,
                                                                                 (bool, bool_)) else Fore.YELLOW
            return f"{Fore.CYAN}{self.name}{Fore.RESET} - " \
                   f"{Style.BRIGHT}{param_color}{self.param}{Fore.RESET}{Style.RESET_ALL}"
        return "[%s] - {%s}" % (self.name, self.param)

