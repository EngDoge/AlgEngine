import os
import gradio as gr

from ..registries import BACKENDS

class BaseApp:
    DEFAULT_CONFIG_NAME: str = None
    CSS: str = None
    
    def __init__(self, 
                 backend: dict,
                 cache_dir: str | None = None,
                 **kwargs):
        self.backend = BACKENDS.build(cfg=backend, recursive=True)
        self.cache_dir = cache_dir
        if cache_dir is not None:
            os.environ['GRADIO_EXAMPLES_CACHE'] = cache_dir
        for k, v in kwargs.items():
            setattr(self, k, v)
            
    def create_service(self) -> gr.Blocks:
        raise NotImplementedError
    
class BaseBackend:
    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    