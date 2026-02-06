from functools import wraps
from time import time, strftime, localtime
from ..logging.supervisor import supervisor


class TimerError(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(message)


class Timer:
    """A flexible Timer class.

    Examples:
        >>> import time
        >>> with Timer():
        >>>     # simulate a code block that will run for 1s
        >>>     time.sleep(1)
        1.000
        >>> with Timer(print_tmpl='it takes {:.1f} seconds'):
        >>>     # simulate a code block that will run for 1s
        >>>     time.sleep(1)
        it takes 1.0 seconds
        >>> timer = mmcv.Timer()
        >>> time.sleep(0.5)
        >>> print(timer.since_start())
        0.500
        >>> time.sleep(0.5)
        >>> print(timer.since_last_check())
        0.500
        >>> print(timer.since_start())
        1.000
    """

    def __init__(self, start=True, print_tmpl=None):
        self._t_start = None
        self._t_last = None
        self._is_running = False
        self.print_tmpl = print_tmpl if print_tmpl else '{:.3f}'
        if start:
            self.start()

    @property
    def is_running(self):
        """bool: indicate whether the timer is running"""
        return self._is_running

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        print(self.print_tmpl.format(self.since_last_check()))
        self._is_running = False

    def start(self):
        """Start the timer."""
        if not self._is_running:
            self._t_start = time()
            self._is_running = True
        self._t_last = time()

    def since_start(self):
        """Total time since the timer is started.

        Returns:
            float: Time in seconds.
        """
        if not self._is_running:
            raise TimerError('timer is not running')
        self._t_last = time()
        return self._t_last - self._t_start

    def since_last_check(self):
        """Time since the last checking.

        Either :func:`since_start` or :func:`since_last_check` is a checking
        operation.

        Returns:
            float: Time in seconds.
        """
        if not self._is_running:
            raise TimerError('timer is not running')
        dur = time() - self._t_last
        self._t_last = time()
        return dur


_g_timers = {}  # global timers


def check_time(timer_id):
    """Add check points in a single line.

    This method is suitable for running a task on a list of items. A timer will
    be registered when the method is called for the first time.

    Examples:
        >>> import time
        >>> for i in range(1, 6):
        >>>     # simulate a code block
        >>>     time.sleep(i)
        >>>     check_time('task1')
        2.000
        3.000
        4.000
        5.000

    Args:
        timer_id (str): Timer identifier.
    """
    if timer_id not in _g_timers:
        _g_timers[timer_id] = Timer()
        return 0
    else:
        return _g_timers[timer_id].since_last_check()


class TimeBenchMark:
    def __init__(self, prefix=None):
        """
        """
        self.prefix = prefix

    def duration(self):
        duration = "Time: %.4f sec" % (time() - self.start)
        # supervisor.info(f"{self.prefix}, {duration}" if self.prefix else duration)
        supervisor.info(f"{self.format_prefix} {duration}" if self.prefix else duration)

    @property
    def format_prefix(self):
        if len(self.prefix) >= 50:
            return self.prefix
        return f"{self.prefix + ' ':·<50}"

    def __enter__(self):
        self.start = time()

    def __exit__(self, *args):
        self.duration()


def get_time_str() -> str:
    return strftime('%Y%m%d_%H%M%S', localtime())


def _procedure(func, info=None):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with TimeBenchMark(func.__name__ if info is None else info):
            ret = func(*args, **kwargs)
        return ret
    return wrapper


def procedure(func=None, info=None):
    if func is None:
        return lambda x: _procedure(func=x, info=info)
    return _procedure(func, info)
