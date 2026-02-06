import os
import cv2

import numpy as np
from tqdm import tqdm
from typing import Union, Optional


from .mappers import ClassMapper
from .container import DataContainer


class ImageConvertor:
    idx_map = np.zeros(16777216, dtype=np.uint32) - 1  # 256 * 256 * 256
    weights = np.array([65536, 256, 1], dtype=np.int32)  # 256 * 256, 256, 1

    def __init__(self,
                 data: Union[DataContainer, str],
                 color_map: Union[ClassMapper, dict],
                 ignore_ref: bool = True,
                 ignore_gerb: bool = True):

        if isinstance(data, str):
            data = DataContainer.from_scan_dir(src=data, ignore_ref=ignore_ref, ignore_gerb=ignore_gerb)

        assert isinstance(data, DataContainer), f'data must be a DataContainer, {type(data)} is given'

        if isinstance(color_map, ClassMapper):
            color_map = color_map.bgr_to_idx
        elif isinstance(color_map, dict):
            print('Caution: color_map should be in BGR color space!')

        self.data = DataContainer.merge_cluster(data, 'image')

        self.color_mapper = color_map

    @staticmethod
    def color2idx(img: np.ndarray, color_map: dict, require_color_in_mapper: bool = True):
        # img and color_map should be in the same color space
        img_shape = img.shape
        assert 3 <= len(img_shape) <= 4, f'img shape should be (H, W, C) or (N, H, W, C), got {img_shape}'
        img = img[..., :3]
        assert img_shape[-1] == 3, f'img given must be RGB or BGR, given channel number of {img_shape}'

        for color, idx in color_map.items():
            ImageConvertor.idx_map[np.dot(color, ImageConvertor.weights)] = idx
        img_id = ImageConvertor.idx_map[np.dot(img, ImageConvertor.weights)]
        if np.any(img_id == 4294967295) and require_color_in_mapper:
            raise ValueError(f'img has some colors not in color_map!')
        return np.uint8(img_id.copy())

    def __getitem__(self, item):
        img = self.data['image'][item]
        img.enable_single_image()
        img.mask.open_with_color()
        try:
            mask_id = self.color2idx(img.mask.image, self.color_mapper)
        except ValueError:
            raise ValueError(f'{img.path} has some colors not in color_map!')
        save_path = img.get_renamed_path('png', 'id')
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        cv2.imwrite(save_path, mask_id.astype(np.uint8))
        return 0

    def __len__(self):
        return self.data.total_num

    def convert(self, batch_size=6, num_workers=6):
        import torch
        from torch.utils.data import Dataset


        class Temp(Dataset, type(self)):
            def __getitem__(self, item):
                return super(Temp, self).__getitem__(item)


        temp_dataset = Temp(data=self.data, color_map=self.color_mapper)
        dataloader = torch.utils.data.DataLoader(temp_dataset,
                                                 batch_size=batch_size,
                                                 shuffle=False,
                                                 num_workers=num_workers)
        pbar = tqdm([i for i in range(self.data.total_num // batch_size)])
        for _ in dataloader:
            pbar.update(1)