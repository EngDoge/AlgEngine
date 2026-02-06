from functools import wraps
from typing import Dict, Any

from .debug import debug_manager

class StatusCollector:
    def __init__(self):  # default to align with debug_manager.debug_mode
        self.status = dict()
        self.log_path = None

    def collect(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            status, conditions = func(*args, **kwargs)
            if debug_manager.status_log:
                processor = args[0].__class__.__name__

                self.status.update(
                    StatusCollector.format_status_log(processor=processor,
                                                      status=status,
                                                      conditions=conditions)
                )

            return status
        return wrapper

    def set_log_path(self, path):
        self.log_path = path

    @staticmethod
    def format_status_log(processor: str,
                          status: Any,
                          conditions: Dict) -> Dict:
        return {processor: {'status': status,
                            'conditions': conditions}}


status_collector = StatusCollector()

