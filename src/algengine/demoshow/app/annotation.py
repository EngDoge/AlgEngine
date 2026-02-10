
import uuid
import numpy as np
import gradio as gr

from .base import BaseApp, BaseBackend
from ..registries import GRADIO_SERVICES, BACKENDS
from ...data import DataContainer


@GRADIO_SERVICES.register_module('annotation_app')
class AnnotationApp(BaseApp):
    DEFAULT_CONFIG_NAME = 'ANNOTATION_CONFIG'
    CSS = ".image-container, .gradio-container, .default {background-color: black; color: black;}"
    def create_service(self):
        with gr.Blocks(title="标注工具") as demo:
            user = gr.State(value=uuid.uuid4())
            image_display = gr.Image(
                label="当前图片",
                value=self.backend.update_image_display(user=user.value),
                height=800
            )
            
            # 功能按钮区域
            with gr.Row():
                disqualify_btn = gr.Button("❌ 不合格", variant="secondary")
                qualified_btn = gr.Button("✅ 合格", variant="primary")
                next_btn = gr.Button("➡️ 下一张", variant="stop")
            refresh_btn = gr.Button("🔁 刷新", variant="stop")
            
            # 按钮事件绑定
            qualified_btn.click(
                fn=self.backend.qualify_image,
                inputs=[user],
                outputs=[image_display]
            )
            
            disqualify_btn.click(
                fn=self.backend.disqualify_image,
                inputs=[user],
                outputs=[image_display]
            )
            
            next_btn.click(
                fn=self.backend.update_image_display,
                inputs=[user],
                outputs=[image_display]
            )
            
            refresh_btn.click(
                fn=self.backend.refresh_image,
                inputs=[user],
                outputs=[image_display]
            )
        
        return demo
    
@BACKENDS.register_module("annotation_backend")    
class AnnotationBackend(BaseBackend):
    def __init__(self, review_path, export_path=None, *args, **kwargs):
        self.review_path = review_path
        self.export_path = export_path
        self.data = DataContainer.from_scan_dir(review_path)
        self.queue = iter(self._next_image())
        self._user_cache = {}
        
    def _next_image(self):
        for data in self.data:
            if not data.info or "label" not in data.info.keys():
                yield data
                
    def next_user_image(self, user):
        try:
            self._user_cache[user] = next(self.queue)
        except StopIteration:
            self._user_cache[user] = None
        
    def current_user_image(self, user):
        try:
            return self._user_cache[user]
        except KeyError:
            return None
    
    def update_image_display(self, user: str):
        self.next_user_image(user=user)
        if user not in self._user_cache or self._user_cache[user] is None:
            return np.ones((100, 100), dtype=np.uint8) * 255
        return self._user_cache[user].cur.path
    
    def qualify_image(self, user: str):
        img_data = self.current_user_image(user)
        if img_data is not None:
            img_data.update_annotation({"label": "OK"})
        return self.update_image_display(user=user)
    
    def disqualify_image(self, user: str):
        img_data = self.current_user_image(user)
        if img_data is not None:
            self.current_user_image(user).update_annotation({"label": "NG"})
        return self.update_image_display(user=user)
    
    def refresh_image(self, user: str):
        self.data = DataContainer.from_scan_dir(self.review_path)
        self.queue = iter(self._next_image())
        return self.update_image_display(user=user)