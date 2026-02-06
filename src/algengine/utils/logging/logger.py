import logging
import colorlog
import os
import gzip
import shutil


ROOT_LOGGER = 'algengine'

logger_initialized: dict = {}

log_colors_config = {
    'DEBUG': 'white',  # cyan white
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}

detailed_log_format = ("[%(asctime)s][%(process)d][%(module)s]"
                       "[%(levelname)s][%(filename)s: %(lineno)d][%(funcName)s] %(message)s")

detailed_color_log_format = f"%(log_color)s{detailed_log_format}"

simple_log_format = "[%(asctime)s][%(process)d][%(levelname)s] %(message)s"

simple_color_log_format = f"%(log_color)s{simple_log_format}"


def set_root_logger(name: str):
    assert isinstance(name, str), f'Logger name must be str, {type(name)} is given!'
    global ROOT_LOGGER
    ROOT_LOGGER = name


def get_logger(name,
               log_file=None,
               log_level=logging.INFO,
               file_mode='w',
               detail_log=False):
    """

    Args:
        name (str): Logger name.
        log_file (str | None): The log filename. If specified, a FileHandler
            will be added to the logger.
        log_level (int): The logger level. Note that only the process of
            rank 0 is affected, and other processes will set the level to
            "Error" thus be silent most of the time.
        file_mode (str): The file mode used in opening log file.
            Defaults to 'w'.
        detail_log (bool): Whether to use detailed logging information.

    Returns:
        logging.Logger: The expected logger.
    """

    logger = logging.getLogger(name)
    logger.propagate = False
    if name in logger_initialized:
        return logger

    for logger_name in logger_initialized:
        if name.startswith(logger_name):
            return logger

    for handler in logger.root.handlers:
        if type(handler) is logging.StreamHandler:
            handler.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler()
    handlers = [stream_handler]

    output_format = detailed_color_log_format if detail_log else simple_color_log_format
    if log_file is not None:
        file_handler = logging.FileHandler(log_file, file_mode)
        file_handler.setFormatter(logging.Formatter(output_format))
        handlers.append(file_handler)

    formatter = colorlog.ColoredFormatter(output_format, log_colors=log_colors_config)
    for handler in handlers:
        handler.setFormatter(formatter)
        handler.setLevel(log_level)
        logger.addHandler(handler)

    logger.setLevel(logging.DEBUG)

    logger_initialized[name] = True

    return logger


def get_root_logger(log_file=None,
                    log_level=logging.INFO):
    """Get root logger.

        Args:
            log_file (str, optional): File path of log. Defaults to None.
            log_level (int, optional): The level of logger.
                Defaults to :obj:`logging.INFO`.

        Returns:
            :obj:`logging.Logger`: The obtained logger
        """
    return get_logger(ROOT_LOGGER, log_file, log_level)


def print_log(msg, logger=None, level=logging.INFO):
    """Print a log message.

    Args:
        msg (str): The message to be logged.
        logger (logging.Logger | str | None): The logger to be used.
            Some special loggers are:

            - "silent": no message will be printed.
            - other str: the logger obtained with `get_root_logger(logger)`.
            - None: The `print()` method will be used to print log messages.
        level (int): Logging level. Only available when `logger` is a Logger
            object or "root".
    """
    if logger is None:
        print(msg)
    elif isinstance(logger, logging.Logger):
        logger.log(level, msg)
    elif logger == 'silent':
        pass
    elif isinstance(logger, str):
        _logger = get_logger(logger)
        _logger.log(level, msg)
    else:
        raise TypeError(
            'logger should be either a logging.Logger object, str, '
            f'"silent" or None, but got {type(logger)}')


def rotator(src, dst):
    with open(src, 'rb') as f_in:
        with gzip.open(dst, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    os.remove(src)


def namer(name):
    return f"{name}.gz"

