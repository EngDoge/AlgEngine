from typing import Sequence, Dict
from abc import ABCMeta, abstractmethod

import numpy as np
import torch.nn as nn


from ...logging import supervisor

class BaseWrapper(nn.Module, metaclass=ABCMeta):
    def __init__(self, output_names: Sequence[str] | None = None):
        super().__init__()
        self._output_names = output_names

    @property
    def output_names(self) -> Sequence[str]:
        return self._output_names
    
    @output_names.setter
    def output_names(self, value: Sequence[str]):
        self._output_names = value
    
    @abstractmethod
    def forward(self, inputs: Dict[str, np.ndarray]):
        pass
    
    def warm_up(self, round: int):
        supervisor.warning(f"warm_up is not implemented for {type(self)}")