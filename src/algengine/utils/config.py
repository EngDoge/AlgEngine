import os
import json
import yaml
from pprint import pformat
from pathlib import Path

import numpy as np

def set_default(obj):
    """Set default json values for non-serializable values.

    It helps convert ``set``, ``range`` and ``np.ndarray`` data types to list.
    It also converts ``np.generic`` (including ``np.int32``, ``np.float32``,
    etc.) into plain numbers of plain python built-in types.
    """
    if isinstance(obj, (set, range)):
        return list(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.generic):
        return obj.item()
    raise TypeError(f'{type(obj)} is unsupported for json dump')

class Config(dict):
    def __init__(self, d=None, **kwargs):
        if d is None:
            d = {}
        else:
            d = dict(d)        
        if kwargs:
            d.update(**kwargs)
        for k, v in d.items():
            setattr(self, k, v)
        # Class attributes
        for k in self.__class__.__dict__.keys():
            if not (k.startswith('__') and k.endswith('__')) and k not in ('update', 'pop'):
                setattr(self, k, getattr(self, k))

    def __setattr__(self, name, value):
        if isinstance(value, (list, tuple)):
            value = type(value)(self.__class__(x)
                     if isinstance(x, dict) else x for x in value)
        elif isinstance(value, dict) and not isinstance(value, Config):
            value = Config(value)
        super(Config, self).__setattr__(name, value)
        super(Config, self).__setitem__(name, value)

    __setitem__ = __setattr__

    def update(self, e=None, **f):
        d = e or dict()
        d.update(f)
        for k in d:
            setattr(self, k, d[k])

    def pop(self, k, *args):
        if hasattr(self, k):
            delattr(self, k)
        return super(Config, self).pop(k, *args)
    
    @classmethod
    def from_json(cls, file):
        with open(os.path.expanduser(file), 'r') as f:
            return cls(json.load(file))
        
    @classmethod
    def from_yaml(cls, file):
        with open(os.path.expanduser(file), 'r') as f:
            return cls(yaml.safe_load(f))
        
    @classmethod
    def from_file(cls, file):
        suffix = Path(file).suffix
        if suffix in ['.xml', '.yaml']:
            return cls.from_yaml(file)
        elif suffix in ['.json', '.jsonl']:
            return cls.from_json(file)
        else:
            raise NotImplementedError(f"Not Supported File Type ({suffix})")
    
    def to_file(self, file, overwrite=False, **kwargs):
        suffix = Path(file).suffix
        if suffix in ['.xml', '.yaml']:
            return self.to_yaml(file=file, overwrite=overwrite, **kwargs)
        elif suffix in ['.json', '.jsonl']:
            return self.to_json(file, overwrite=overwrite, **kwargs)
        else:
            raise NotImplementedError(f"Not Supported File Type ({suffix})")
    
    def _export_to_file(self, file, func, overwrite=False, **kwargs):
        if not overwrite and os.path.exists(file):
            raise FileExistsError(f"Cannot Export To JsonFile: {file}")
        
        file = Path(file)
        os.makedirs(file.parent, exist_ok=True)
        with open(file, 'w') as f:
            func(self.to_dict(), f, **kwargs)
            
    def to_json(self, file, overwrite=False, **kwargs):
        self._export_to_file(file=file, func=json.dump, overwrite=overwrite, default=set_default, **kwargs)
            
    def to_yaml(self, file, overwrite=False, **kwargs):
        self._export_to_file(file=file, func=yaml.dump, overwrite=overwrite, **kwargs)
    
    def to_dict(self):
        return {k: v.to_dict() if isinstance(v, Config) else v for k, v in self.items() if not callable(v)}
    
    def __str__(self):
        return json.dumps(self.to_dict(), indent=4)
    
    def __repr__(self):
        return pformat(self.to_dict())
    
    
    