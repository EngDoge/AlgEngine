class DebugManager:
    def __init__(self,
                 debug_mode: bool = False,
                 status_log: bool = True,
                 color_mode: bool = True):
        self._debug_mode = debug_mode
        self._status_log = status_log
        self._color_mode = color_mode

    def enable_debug(self):
        self._debug_mode = True

    def disable_debug(self):
        self._debug_mode = False

    def enable_color_print(self):
        self._color_mode = True

    def disable_color_print(self):
        self._color_mode = False

    def enable_status_log(self):
        self._status_log = True

    def disable_status_log(self):
        self._status_log = False

    @property
    def debug_mode(self):
        return self._debug_mode

    @property
    def color_mode(self):
        return self._color_mode

    @property
    def status_log(self):
        return self._status_log


debug_manager = DebugManager(debug_mode=False, status_log=False)