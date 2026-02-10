import os
import torch
import random
import glob

import random, string
from PIL import Image
import gradio as gr

from datetime import datetime



from .base import BaseApp, BaseBackend
from ..registries import GRADIO_SERVICES, BACKENDS


AZIMUTH_MAP = {
    0: "front view",
    45: "front-right quarter view",
    90: "right side view",
    135: "back-right quarter view",
    180: "back view",
    225: "back-left quarter view",
    270: "left side view",
    315: "front-left quarter view"
}

# Elevation mappings (4 positions)
ELEVATION_MAP = {
    -30: "low-angle shot",
    0: "eye-level shot",
    30: "elevated shot",
    60: "high-angle shot"
}

# Distance mappings (3 positions)
DISTANCE_MAP = {
    0.6: "close-up",
    1.0: "medium shot",
    1.8: "wide shot"
}

def snap_to_nearest(value, options):
    """Snap a value to the nearest option in a list."""
    return min(options, key=lambda x: abs(x - value))


def build_camera_prompt(azimuth: float, elevation: float, distance: float) -> str:
    """
    Build a camera prompt from azimuth, elevation, and distance values.
    
    Args:
        azimuth: Horizontal rotation in degrees (0-360)
        elevation: Vertical angle in degrees (-30 to 60)
        distance: Distance factor (0.6 to 1.8)
    
    Returns:
        Formatted prompt string for the LoRA
    """
    # Snap to nearest valid values
    azimuth_snapped = snap_to_nearest(azimuth, list(AZIMUTH_MAP.keys()))
    elevation_snapped = snap_to_nearest(elevation, list(ELEVATION_MAP.keys()))
    distance_snapped = snap_to_nearest(distance, list(DISTANCE_MAP.keys()))
    
    azimuth_name = AZIMUTH_MAP[azimuth_snapped]
    elevation_name = ELEVATION_MAP[elevation_snapped]
    distance_name = DISTANCE_MAP[distance_snapped]
    
    return f"<sks> {azimuth_name} {elevation_name} {distance_name}"

    
@GRADIO_SERVICES.register_module('multi_angle_app')
class MultiAngleApp(BaseApp):

    DEFAULT_CONFIG_NAME = 'MULTI_ANGLE_CONFIG'
    CSS = '''
    #col-container { max-width: 1200px; margin: 0 auto; }
    .dark .progress-text { color: white !important; }
    .slider-row { display: flex; gap: 10px; align-items: center; }
    '''
    
    def get_examples(self):
        return [[img] for img in sorted(glob.glob(f"{self.example_root}/*.*"))]
    
    def create_service(self):
        with gr.Blocks(title='多视角生成Demo') as service:
            gr.Markdown(self.title)
            with gr.Row(equal_height=True):
                with gr.Column(scale=1):
                    input_image = gr.Image(label="输入图像", type="pil")
                with gr.Column(scale=2):
                    result_image = gr.Image(label="生成图像", height=500)
                    
            run_btn = gr.Button("🚀 生成", variant="primary", size="lg")
            
            run_btn.click(
                fn=self.backend,
                inputs=[input_image],
                outputs=[result_image]
            )
            
            gr.Examples(
                examples=self.get_examples(),
                inputs = [input_image],
                outputs=[result_image],
                fn=self.backend,
                cache_examples=True,
                cache_mode='lazy', # eager for precompute
                examples_per_page=20,
            )
                
        return service

@BACKENDS.register_module("multi_angle_backend")    
class MultiAngleBackend(BaseBackend):
    def __init__(self, 
                 base_model_path: str = "Qwen/Qwen-Image-Edit-2511",
                 lightning_lora_root: str = 'lightx2v/Qwen-Image-Edit-2511-Lightning',
                 multi_angle_lora_root: str = 'fal/Qwen-Image-Edit-2511-Multiple-Angles-LoRA',
                 export_dir: str | None = None,
                #  base_model_path: str,
                #  lightning_lora_root: str,
                #  multi_angle_lora_root: str,
                 *args, **kwargs):
        from diffusers import QwenImageEditPlusPipeline
        
        self.dtype = torch.bfloat16
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        pipe = QwenImageEditPlusPipeline.from_pretrained(
            base_model_path,
            torch_dtype=self.dtype
        ).to(self.device)
        
        pipe.load_lora_weights(
            lightning_lora_root,
            weight_name="Qwen-Image-Edit-2511-Lightning-4steps-V1.0-bf16.safetensors",
            adapter_name="lightning"
        )
        
        pipe.load_lora_weights(
            multi_angle_lora_root,
            weight_name="qwen-image-edit-2511-multiple-angles-lora.safetensors",
            adapter_name="angles"
        )
        
        pipe.set_adapters(["lightning", "angles"], adapter_weights=[1.0, 1.0])
        self.pipe = pipe
        self.export_dir = export_dir

    @staticmethod
    def sample_n_prompts(n: int = 4):
        azi_opt = [0, 45, 90, 270, 315]
        ele_opt = [0, -30, 30, 60]
        dist_opt = [1.0, 0.6, 1.8]

        len_azi = len(azi_opt)
        len_ele = len(ele_opt)
        len_dist = len(dist_opt)

        result = []
        tmp = []
        do_sample = True
        while do_sample:
            target = random.randint(1, len_azi * len_ele * len_azi - 1)
            if target not in tmp:
                tmp.append(target)
                if len(tmp) == n:
                    do_sample = False
            else:
                continue
            params = (azi_opt[target % len_azi], 
                    ele_opt[target % len_ele],
                    dist_opt[target % len_dist])
            result.append(build_camera_prompt(*params))
        return result

    @staticmethod
    def result_layout(input_image: Image.Image, result_images: list[Image.Image]):
        w, h = input_image.size
        half_w, half_h = w // 2, h // 2
        canvas_size = (half_w * 4, h)
        
        concat_image = Image.new("RGB", canvas_size)
        concat_image.paste(input_image, (0, 0))
        
        for i, img in enumerate(result_images):
            concat_image.paste(img.resize((half_w, half_h)), 
                               (w + (i % 2) * half_w, (i // 2) * half_h))
        
        return concat_image
    
    
    @staticmethod
    def random_str(length):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
    
    @staticmethod
    def date_str():
        return datetime.now().strftime("%Y%m%d")
    
    def __call__(self, image):
        if image is None:
            raise gr.Error("Please upload an image first.")
        
        prompts = self.sample_n_prompts(n=4)
        result_images = [
                self.pipe(
                    image=image,
                    prompt=prompt,
                    # height=height if height != 0 else None,
                    # width=width if width != 0 else None,
                    num_inference_steps=4,
                    generator=torch.Generator(device=self.device).manual_seed(42),
                    num_images_per_prompt=1,
                    # guidance_scale=guidance_scale,
                ).images[0] for prompt in prompts   
            ]
        result = self.result_layout(
            input_image=image,
            result_images=result_images
        )
        name = self.random_str(8)
        if self.export_dir is not None:
            save_root = os.path.join(self.export_dir, self.date_str())
            os.makedirs(save_root, exist_ok=True)
            for i, img in enumerate(result_images):
                img.save(f"{save_root}/{name}_{"_".join(prompts[i].split(' ')[1:])}.png")
        return result
        
