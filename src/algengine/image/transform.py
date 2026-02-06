import numpy as np
from PIL import Image
from ..utils import Registry

TRANSFORMS = Registry('Transforms')


class BaseTransform:
    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
            
    def __call__(self, image: np.ndarray | Image.Image, *args, **kwargs):
        raise NotImplementedError