
import time
import base64

import cv2
import requests
from io import BytesIO
from pathlib import Path
from typing import Union, Dict, Optional, Tuple, Literal

import numpy as np
from PIL import Image

from .misc import convert2map, is_url

BACKEND_ALIAS = convert2map({
    'cv2': ['cv2', 'opencv', 'opencv-python'],
    'pillow': ['pillow', 'PIL', 'pil'],
    'base64': ['base64']
})


def image2ndarray(image: Image.Image, mode: Optional[str] = 'BGR') -> np.ndarray:
    """
    Convert Image.Image to np.ndarray, the output array is in BGR by default.
    """
    if isinstance(image, Image.Image):
        if mode is None or mode == 'BGR':
            return np.asarray(image.convert('RGB'))[..., ::-1]
        elif mode == 'RAW':
            return np.asarray(image)
        else:
            return np.asarray(image.convert(mode))
    elif isinstance(image, np.ndarray):
        if mode == "L":
            return (image if image.ndim == 2 else
                    cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY if image.shape[2] == 4 else cv2.COLOR_BGR2GRAY))
        return image if ((mode is None) or (mode == 'BGR') or (mode == 'RAW')) else image[..., ::-1]
    else:
        raise ValueError(f'Image.Image expected, got {type(image)}')

def ndarray2image(array: np.ndarray, mode: Optional[str] = 'RGB') -> Image.Image:
    """
    Convert np.ndarray to Image.Image, array should be in BGR.
    """
    if isinstance(array, np.ndarray):
        if mode is None:
            return Image.fromarray(array[..., ::-1], mode="RGB")
        elif mode == 'RAW':
            return Image.fromarray(array)
        elif mode == "L":
            return (Image.fromarray(array, mode="L")
                    if array.ndim == 2 else
                    Image.fromarray(
                        cv2.cvtColor(array, cv2.COLOR_BGRA2GRAY if array.shape[2] == 4 else cv2.COLOR_BGR2GRAY),
                        mode="L")
                    )
        return Image.fromarray(array[..., ::-1], mode="RGB").convert(mode)
    elif isinstance(array, Image.Image):
        return array if (mode is None or mode == "RAW") else array.convert(mode)
    else:
        raise ValueError(f'np.ndarray expected, got {type(array)}')

def image2base64(image: Image.Image, file_type: Literal['PNG', 'JPEG'] = 'PNG', **kwargs) -> str:
    buffered = BytesIO()
    file_type = "PNG" if image.mode == 'RGBA' else file_type
    image.save(buffered, format=file_type)
    return base64.b64encode(buffered.getvalue()).decode()


def paste_on_background(image: Image.Image,
                        color: Union[int, Tuple[int, int, int]] = (255, 255, 255),
                        mode: Optional[str] = None) -> Image.Image:
    if isinstance(color, int):
        color = (color, color, color)
    *_, a = image.split()
    bg = Image.new(image.mode, image.size, color)
    bg.paste(image, mask=a)
    return bg if mode is None else bg.convert(mode)

def load_from(image: Union[str, Path, np.ndarray, Image.Image],
              backend: str = 'pillow',
              white_background: bool = False,
              headers: Optional[Dict] = None,
              retry: int = 2,
              sleep: float = 0.5,
              mode: Optional[str] = 'RGB',
              *args, **kwargs) -> Union[np.ndarray, Image.Image, str]:
    """Load image from path or url.

    Args:
        image: (str) path or url of image
        backend: (str) 'pillow' or 'cv2', default 'pil'
        white_background: (bool) whether convert RGBA image to RGB image with white background
        headers: (optional[dict]) headers for requests
        retry: (int) retry times for loading image
        sleep: (float) sleep time between retries
        mode: (str) mode of image, default 'RGB'

    Returns:
        image: (np.ndarray or Image.Image) image loaded, mode by default 'RGB'
    """

    if isinstance(image, Path):
        image = str(image)

    if isinstance(image, (str, bytes)):
        if isinstance(image, bytes):
            image = BytesIO(base64.b64decode(image))
        elif is_url(image):
            trail = 0
            while trail <= retry:
                try:
                    image = BytesIO(requests.get(image, headers=headers, stream=True).content)
                except:
                    if trail < retry:
                        time.sleep(sleep)
                        trail += 1
                        continue
                    raise TimeoutError(f'Failed to load image from {image}')
                break
        else:
            try:
                image = BytesIO(base64.b64decode(image, validate=True))
            except Exception as e:
                pass
        image = Image.open(image)

        if white_background and (image.mode == 'RGBA'):
            image = paste_on_background(image, color=(255, 255, 255))

    backend = BACKEND_ALIAS[backend]

    if 'base64' in backend:
        return image2base64(image=ndarray2image(image, mode=mode), **kwargs)
    if isinstance(image, (Image.Image, np.ndarray)):
        return ndarray2image(image, mode=mode) if 'pillow' in backend else image2ndarray(image, mode=mode)
    raise ValueError(f'Invalid path type: {type(image)}')

