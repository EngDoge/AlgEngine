import torch

from diffusers.models import AutoencoderKL
from diffusers.utils.torch_utils import randn_tensor

class FluxUtils:
    @staticmethod
    def pack_latents(latents: torch.Tensor):
        """
        Pack the latents from BCHW to BLC
        """
        B, C, H, W = latents.shape
        latents = latents.view(B, C, H // 2, 2, W // 2, 2)
        latents = latents.permute(0, 2, 4, 1, 3, 5)
        latents = latents.reshape(B, (H // 2) * (W // 2), C * 4)
        return latents

    @staticmethod
    def unpack_latents(latents, height, width, downsample_factor: int = 8):
        """
        Unpack latents from BLC to BCHW
        
        height & width are the original height and width of image
        """
        B, _, C = latents.shape
        height = 2 * (int(height) // (downsample_factor * 2))
        width = 2 * (int(width) // (downsample_factor * 2))

        latents = latents.view(B, height // 2, width // 2, C // 4, 2, 2)
        latents = latents.permute(0, 3, 1, 4, 2, 5)

        latents = latents.reshape(B, C // (2 * 2), height, width)

        return latents
    
    @staticmethod
    def decode_latents(vae: AutoencoderKL, latents, height, width, downsample_factor: int = 8, postprocessor=None):
        latents = FluxUtils.unpack_latents(latents, height, width, downsample_factor)
        latents = (latents / vae.config.scaling_factor) + vae.config.shift_factor
        image = vae.decode(latents, return_dict=False)[0]
        return postprocessor(image) if postprocessor is not None else image
        
    @staticmethod
    def encode_images(vae: AutoencoderKL, images: torch.Tensor, preprocessor=None):
        if preprocessor is not None:
            images = preprocessor(images)
        _module = next(vae.encode.parameters())
        images = images.to(dtype=_module.dtype, device=_module.device)
        images = vae.encode(images).latent_dist.sample()
        images = (images - vae.config.shift_factor) * vae.config.scaling_factor
        
        H, W = images.shape[2], images.shape[3]
        latents = FluxUtils.pack_latents(images)
        latent_ids = FluxUtils.prepare_latent_ids(H, W)
        
        return latents, latent_ids
    
    @staticmethod
    def prepare_latent_ids(H, W):
        latent_ids = torch.zeros(H, W, 3)
        latent_ids[..., 1] = latent_ids[..., 1] + torch.arange(H)[:, None]
        latent_ids[..., 2] = latent_ids[..., 2] + torch.arange(W)[None, :]

        latent_ids = latent_ids.reshape(H * W, 3)

        return latent_ids
    
    @staticmethod
    def prepare_latents(
        height,
        width,
        generators: list[torch.Generator] | torch.Generator,
        batch_size: int = 1,
        num_channels: int = 16,
        downsample_factor: int = 8,
        latents: torch.Tensor | None = None
    ):
        H = 2 * (int(height) // (downsample_factor * 2))
        W = 2 * (int(width) // (downsample_factor * 2))
        
        shape = (batch_size, num_channels, H, W)

        if latents is None:
            if isinstance(generators, list) and len(generators) != batch_size:
                generators = [generators[0]] * batch_size
                
            latents = latents = randn_tensor(shape, generator=generators)
            latents = FluxUtils.pack_latents(latents)
              
        latent_ids = FluxUtils.prepare_latent_ids(H, W)
        return latents, latent_ids

        