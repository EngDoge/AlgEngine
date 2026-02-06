import os
from typing import Union, Optional, Any
from ctypes import cdll, c_char_p

import torch
import tensorrt as trt
import pycuda.driver as _cuda


LIB_CUDART = cdll.LoadLibrary('libcudart.so')
LIB_CUDART.cudaGetErrorString.restype = c_char_p


def create_device_ctx(device_id: int):
    _cuda.init()
    device = _cuda.Device(device_id)
    return device.make_context()

def run_in_context(func):
    def wrapper(self, *args, **kwargs):
        self.ctx.push()
        try:
            result = func(self, *args, **kwargs)
        finally:
            self.ctx.pop()

        return result
    return wrapper

def cuda_set_device(device_idx: int):
    """set cuda device

    Args:
        device_idx (int): Index of CUDA device
    """
    ret = LIB_CUDART.cudaSetDevice(device_idx)
    if ret != 0:
        error_string = LIB_CUDART.cudaGetErrorString(ret)
        raise RuntimeError(f"cuda_set_device: {error_string}")

def save(engine: Any, path: str, make_dir: bool = True) -> None:
    """Serialize TensorRT engine to disk.

    Args:
        engine (Any): TensorRT engine to be serialized.
        path (str): The absolute disk path to write the engine.
        make_dir (bool): Whether to create the directory if it does not exist.
    """
    os.makedirs(os.path.dirname(path), exist_ok=make_dir)
    with open(path, mode='wb') as f:
        if isinstance(engine, trt.ICudaEngine):
            engine = engine.serialize()
        f.write(bytearray(engine))

def load(engine: Union[str, bytes]) -> Optional[trt.ICudaEngine]:
    """Deserialize TensorRT engine from disk.

    Args:
        engine (Optional[str, bytes]): The disk path to read the engine, or byte file of the engine

    Returns:
        tensorrt.ICudaEngine: The TensorRT engine loaded from disk.
    """
    with trt.Logger(trt.Logger.WARNING) as logger, trt.Runtime(logger) as runtime:
        if isinstance(engine, str):
            with open(engine, mode="rb") as f:
                engine_bytes = f.read()
        else:
            engine_bytes = engine
        engine = runtime.deserialize_cuda_engine(engine_bytes)
    return engine


def torch_device_from_trt(device: trt.TensorLocation):
    """Convert pytorch device to TensorRT device.

    Args:
        device (trt.TensorLocation): The device in tensorrt.
    Returns:
        torch.device: The corresponding device in torch.
    """
    if device == trt.TensorLocation.DEVICE:
        return torch.device('cuda')
    elif device == trt.TensorLocation.HOST:
        return torch.device('cpu')
    else:
        return TypeError(f'{device} is not supported by torch')

def torch_dtype_from_trt(dtype: trt.DataType) -> torch.dtype:
    """Convert pytorch dtype to TensorRT dtype.

    Args:
        dtype (str.DataType): The data type in tensorrt.

    Returns:
        torch.dtype: The corresponding data type in torch.
    """

    if dtype == trt.bool:
        return torch.bool
    elif dtype == trt.int8:
        return torch.int8
    elif dtype == trt.int32:
        return torch.int32
    elif dtype == trt.float16:
        return torch.float16
    elif dtype == trt.float32:
        return torch.float32
    else:
        raise TypeError(f'{dtype} is not supported by torch')
