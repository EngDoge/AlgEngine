from collections import defaultdict
from .config import Config



class ActionRecorder:
    def __init__(self, obj_type):
        self.actions = defaultdict(ActionRecorder.default_fn)
        self.obj_type = obj_type

    @staticmethod
    def default_fn():
        return Config(list)

    def items(self):
        for key, value in self.actions.items():
            yield key, value.args, value.kwargs

    def __getitem__(self, item):
        return self.actions[item]

    def duplicate_action(self, obj):
        assert isinstance(obj, self.obj_type), f'Current ActionRecorder only works for {self.obj_type}'
        for action, args, kwargs in self.items():
            for iter_args, iter_kwargs in zip(args, kwargs):
                todo = getattr(obj, action)
                todo(*iter_args, **iter_kwargs)

    def __str__(self):
        ret = '\n'.join([f'{self.obj_type.__name__}.{fn}(*{args}, **{kwargs})'
                         for fn in self.actions
                         for args, kwargs in zip(self.actions[fn].args, self.actions[fn].kwargs)])
        return ret