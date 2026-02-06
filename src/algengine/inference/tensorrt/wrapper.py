from typing import Dict

import torch
import numpy as np
import tensorrt as trt
import cuda as cudart # pip install cuda-python

from .utils import load, create_device_ctx, run_in_context
from ..base import BaseWrapper
from ...utils import parse_device_id



class TRTWrapper(BaseWrapper):
    def __init__(self, 
                 src: str | bytes,
                 device: str = 'cuda',
                 output_names = None):
        
        self.engine = src
        self.ctx = create_device_ctx(parse_device_id(device))
        self.ctx.push()
        if isinstance(self.engine, str) or isinstance(self.engine, bytes):
            self.engine = load(self.engine)
        self.context = self.engine.create_execution_context()
        self.__load_io_names()
        self.ctx.pop()

        super().__init__(output_names)

    def __load_io_names(self):
        """Load input/output names from engine."""
        names = [_ for _ in self.engine]
        try:
            input_names = list(filter(self.engine.binding_is_input, names))
        except AttributeError:
            input_names = [name for name in names if self.engine.get_tensor_mode(name) == trt.TensorIOMode.INPUT]
        self._input_names = input_names

        if self._output_names is None:
            output_names = list(set(names) - set(input_names))
            self._output_names = output_names

    @property
    def input_names(self):
        return self._input_names
    
    @run_in_context
    def forward(self, inputs: list[np.ndarray]| Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        if isinstance(inputs, dict):
            inputs = list(inputs.values())
        nIO = self.engine.num_io_tensors

        nIO = self.engine.num_io_tensors
        lTensorName = [self.engine.get_tensor_name(i) for i in range(nIO)]
        nInput = [self.engine.get_tensor_mode(lTensorName[i]) for i in range(nIO)].count(trt.TensorIOMode.INPUT)

        bufferH = []
        for i in range(nInput):
            input_data = inputs[i]
            self.context.set_input_shape(lTensorName[i], tuple(input_data.shape))
            bufferH.append(np.ascontiguousarray(input_data))

        for i in range(nInput, nIO):
            bufferH.append(np.empty(self.context.get_tensor_shape(lTensorName[i]),
                                    dtype=trt.nptype(self.engine.get_tensor_dtype(lTensorName[i]))))

        bufferD = []
        for i in range(nIO):
            bufferD.append(cudart.cudaMalloc(bufferH[i].nbytes)[1])

        for i in range(nInput):
            cudart.cudaMemcpy(bufferD[i], bufferH[i].ctypes.data,
                              bufferH[i].nbytes,
                              cudart.cudaMemcpyKind.cudaMemcpyHostToDevice)

        for i in range(nIO):
            self.context.set_tensor_address(lTensorName[i], int(bufferD[i]))

        # torch.cuda.synchronize()
        self.context.execute_async_v3(0)
        torch.cuda.synchronize()

        for i in range(nInput, nIO):
            cudart.cudaMemcpy(bufferH[i].ctypes.data, bufferD[i],
                              bufferH[i].nbytes,
                              cudart.cudaMemcpyKind.cudaMemcpyDeviceToHost)

        for b in bufferD:
            cudart.cudaFree(b)

        return dict(zip(lTensorName, bufferH))