DEFAULT_CONFIGS = {
    'MULTI_ANGLE_CONFIG': {
        "type": "multi_angle_app",
        "title": "# 🎬 生成式多视角生成Demo",
        'cache_dir': '/data0/sunjianyao/tools/MultiAngle/example_cache',
        'example_root': '/data0/sunjianyao/tools/MultiAngle/examples',
        
        "backend": {
            'type': "multi_angle_backend",
            'base_model_path': "/data0/sunjianyao/models/Qwen/Qwen-Image-Edit-2511",
            'lightning_lora_root': "/data0/sunjianyao/models/lightx2v/Qwen-Image-Edit-2511-Lightning",
            'multi_angle_lora_root': "/data0/sunjianyao/models/fal/Qwen-Image-Edit-2511-Multiple-Angles-LoRA",
            'export_dir': '/data0/sunjianyao/tools/MultiAngle/export'
        },
    },
    'ANNOTATION_CONFIG': {
        "type": 'annotation_app',
        'example_root': '/data0/sunjianyao/datasets/idphoto/generate/260129_generate_woman/red',
        "backend": {
            'type': "annotation_backend",
            "review_path": '/data0/sunjianyao/datasets/idphoto/generate/260129_generate_woman/red',
        },
    }
}
