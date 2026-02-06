from typing import List, Sequence, Dict, Tuple

import numpy as np
import onnxruntime as ort

from ..base import BaseWrapper
from ...utils import parse_device_id


class ORTWrapper(BaseWrapper):
    def __init__(self, 
                 src: str,
                 device: str | int = 'cpu',
                 output_names: Sequence[str] | None = None,
                 ):
        
        session_options = ort.SessionOptions()

        device_id = parse_device_id(device)
        providers = (['CPUExecutionProvider'] if device == 'cpu' 
                     else [('CUDAExecutionProvider', {'device_id': device_id}), 'CPUExecutionProvider'])
        
        sess = ort.InferenceSession(path_or_bytes=src,
                                    sess_options=session_options,
                                    providers=providers)

        if output_names is None:
            output_names = [_.name for _ in sess.get_outputs()]

        self.onnx_session = sess
        self._meta_inputs = {_.name: _ for _ in sess.get_inputs()}
        # meta_data.type: str | meta_data.name: str | meta_data.shape: List[int|str]

        self._input_names = list(self._meta_inputs.keys())

        self.device_id = device_id
        self.device_type  = 'cpu' if device == 'cpu' else 'cuda'

        super().__init__(output_names)

    @property
    def input_names(self) -> List[str]:
        return self._input_names
    
    def forward(self, inputs: Dict[str, np.ndarray]):
        result = self.onnx_session.run(self._output_names, inputs)
        return {name: val for name, val in zip(self.output_names, result)}
    
    @staticmethod
    def get_warmup_input_shape(meta_info, shape: Tuple | None = None):
        return (dim if isinstance(dim, int) else shape[i] for i, dim in enumerate(meta_info.shape))

    def warm_up(self, round: int = 5, shape: Tuple | None = None, inputs: Dict[str, np.ndarray] | None = None) -> None:
        if inputs is None:
            inputs = {name: np.random.randn(*self.get_warmup_input_shape(meta_info, shape=shape)) 
                      for name, meta_info in self._meta_inputs.items()}
        for _ in range(round):
            _ = self.forward(inputs)
