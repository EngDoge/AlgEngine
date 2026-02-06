from copy import deepcopy
from typing import Tuple, Optional, Dict, NoReturn, List


class ClassMapper:

    # RGB color values
    CODE2ALIAS = dict(
        FASEPARSE={
            "FACE00": ["background"],
            "FACE01": ["face"],
            "FACE02": ["left_eyebrow"],
            "FACE03": ["right_eyebrow"],
            "FACE04": ["left_eye"],
            "FACE05": ["right_eye"],
            "FACE06": ["glasses"],
            "FACE07": ["left_ear"],
            "FACE08": ["right_ear"],
            "FACE09": ["U1"],
            "FACE10": ["nose"],
            "FACE11": ["U2"],
            "FACE12": ["upper_lips"],
            "FACE13": ["lower_lips"],
            "FACE14": ["U3"],
            "FACE15": ["clothes"],
            "FACE16": ["hair"],
        },
    )

    CODE2COLOR = dict(
        FACE={
            "FACE00": [(0, 0, 0)],
            "FACE01": [(255, 182, 193)],
            "FACE02": [(220, 20, 60)],
            "FACE03": [(219, 112, 147)],
            "FACE04": [(255, 105, 180)],
            "FACE05": [(199, 21, 133)],
            "FACE06": [(218, 112, 214)],
            "FACE07": [(216, 191, 216)],
            "FACE08": [(221, 160, 221)],
            "FACE09": [(255, 0, 255)],
            "FACE10": [(128, 0, 128)],
            "FACE11": [(75, 0, 130)],
            "FACE12": [(138, 43, 226)],
            "FACE13": [(123, 104, 238)],
            "FACE14": [(230, 230, 250)],
            "FACE15": [(0, 0, 255)],
            "FACE16": [(25, 25, 112)],
            # "FACE17": [(65, 105, 225)],
            # "FACE18": [(176, 196, 222)],
            # "FACE19": [(119, 136, 153)],
            # "FACE20": [(155, 42, 42)],
            # "FACE21": [(200, 0, 0)],
            # "FACE22": [(30, 144, 255)],
            # "FACE23": [(96, 60, 226)],
            # "FACE24": [(70, 130, 180)],
            # "FACE25": [(0, 191, 255)],
            # "FACE26": [(95, 158, 160)],
            # "FACE27": [(175, 238, 238)],
            # "FACE28": [(0, 255, 255)],
            # "FACE29": [(0, 206, 209)],
            # "FACE30": [(0, 128, 128)],
            # "FACE31": [(44, 22, 106)],
            # "FACE32": [(127, 255, 170)],
            # "FACE33": [(0, 250, 154)],
            # "FACE34": [(0, 255, 127)],
            # "FACE35": [(60, 179, 113)],
            # "FACE36": [(143, 188, 143)],
            # "FACE37": [(0, 100, 0)],
            # "FACE38": [(124, 252, 0)],
            # "FACE39": [(173, 255, 47)],
            # "FACE40": [(85, 107, 47)],
            # "FACE41": [(245, 245, 220)],
            # "FACE42": [(190, 210, 200)],
            # "FACE43": [(255, 255, 0)],
            # "FACE44": [(189, 183, 107)],
            # "FACE45": [(140, 0, 255)],
            # "FACE46": [(255, 250, 205)],
            # "FACE47": [(170, 150, 18)],
            # "FACE48": [(240, 230, 140)],
            # "FACE49": [(255, 215, 0)],
            # "FACE50": [(255, 228, 181)],
            # "FACE51": [(255, 165, 0)],
            # "FACE52": [(222, 184, 135)],
            # "FACE53": [(205, 133, 63)],
            # "FACE54": [(255, 218, 185)],
            # "FACE55": [(139, 69, 19)],
            # "FACE56": [(255, 160, 122)],
            # "FACE57": [(255, 69, 0)],
            # "FACE58": [(255, 228, 225)],
            # "FACE59": [(255, 150, 200)],
            # "FACE60": [(250, 128, 114)],
            # "FACE61": [(205, 92, 92)],
            # "FACE62": [(255, 0, 0)],
            # "FACE63": [(128, 0, 0)],
            # "FACE64": [(220, 220, 220)],
            # "FACE65": [(169, 169, 169)],
            # "FACE66": [(0, 13, 192)],
        }
    )

    MAPPER_TYPE = list(CODE2COLOR.keys())
    COLOR_TYPE = "RGB"

    __slots__ = ['project_type', 'code2alias', 'code2color', 'merged_idx_mapper']

    def __init__(self,
                 project_type: str,
                 custom_palette: Optional[Dict] = None,
                 update_palette: Optional[Dict] = None,
                 merge_palette: Optional[Dict] = None,
                 **kwargs):

        if project_type not in self.MAPPER_TYPE:
            raise NotImplementedError(f'project_type must be in {self.MAPPER_TYPE}')

        assert len(self.CODE2COLOR[project_type]) == len(self.CODE2ALIAS[project_type]), \
            f'CODE2COLOR({len(self.CODE2COLOR[project_type])}) and ' \
            f'CODE2ALIAS({len(self.CODE2ALIAS[project_type])}) must have same length, '

        self.project_type = project_type
        self.code2alias = None
        self.code2color = None
        self.merged_idx_mapper = None
        self.update_mapper(custom_palette, update_palette, **kwargs)
        self.get_merged_idx_mapper(merge_palette)

    def get_merged_idx_mapper(self, merge_palette: Optional[Dict]) -> NoReturn:
        self.merged_idx_mapper = {i: i for i in range(len(self.code2alias))}
        if merge_palette is not None:
            for key, to_be_merged in merge_palette.items():
                target_key = self.name2idx(key)
                for alias in to_be_merged:
                    ori_idx = self.name2idx(alias)
                    self.merged_idx_mapper[ori_idx] = target_key

    def update_mapper(self,
                      custom_palette: Optional[dict] = None,
                      update_palette: Optional[dict] = None,
                      merge_palette: Optional[dict] = None,
                      **kwargs) -> 'ClassMapper':

        assert not (custom_palette and update_palette), \
            'custom_palette and update_palette cannot be set at the same time'
        if custom_palette is not None:
            self.code2alias = {f'{self.project_type}{i:02d}': [key] for i, key in enumerate(custom_palette.keys())}
            self.code2color = {f'{self.project_type}{i:02d}': value for i, value in enumerate(custom_palette.values())}
        else:
            self.code2alias = deepcopy(self.CODE2ALIAS[self.project_type])
            self.code2color = deepcopy(self.CODE2COLOR[self.project_type])
            if update_palette is not None:
                for code, alias in self.code2alias.items():
                    intersection = set(alias) & set(update_palette.keys())
                    if intersection:
                        if len(intersection) > 1:
                            raise ValueError(f'alias {alias} has more than one intersection with update_palette')
                        self.code2color[code] = update_palette[list(intersection)[0]]
        self.get_merged_idx_mapper(merge_palette)
        return self
    
    def code2idx(self, code: str) -> int:
        return self.merged_idx_mapper[int(code[-2:])]
    
    def name2idx(self, name) -> int:
        return self.code2idx(self.name2code(name))
    
    def name2code(self, name) -> str:
        for code, alias in self.code2alias.items():
            if name in alias:
                return code
        raise ValueError('name not in class mapper')

    def name2color(self, name: str) -> Tuple[int, int, int]:
        for code, alias in self.code2alias.items():
            if name in alias:
                return self.code2color[code][0]
        raise ValueError('name not in class mapper')

    def idx2name(self, idx: int) -> str:
        return self.code2alias[f'{self.project_type}{idx:02d}'][0]

    def idx2color(self, idx: int) -> Tuple[int, int, int]:
        return self.code2color[f'{self.project_type}{idx:02d}'][0]

    def color2idx(self, color: Tuple) -> int:
        for code, colors in self.code2color.items():
            if color in colors:
                return self.code2idx(code)
        raise ValueError(f'color({color}) not in class mapper')

    @property
    def classes(self) -> List[str]:
        return [self.idx2name(k) for k, v in self.merged_idx_mapper.items() if k == v]
    
    @property
    def palettes(self) -> List[Tuple[int, int, int]]:
        return [self.idx2color(k) for k, v in self.merged_idx_mapper.items() if k == v]

    @property
    def num_classes(self) -> int:
        return len(self.code2alias)

    @property
    def rgb_to_idx(self) -> Dict[Tuple[int, int, int], int]:
        return {color: self.code2idx(code) for code, colors in self.code2color.items() for color in colors}

    @property
    def bgr_to_idx(self) -> Dict[Tuple[int, int, int], int]:
        return {color[::-1]: self.code2idx(code) for code, colors in self.code2color.items() for color in colors}

    @property
    def alias_to_idx(self) -> Dict[str, int]:
        return {name: self.code2idx(code) for code, alias in self.code2alias.items() for name in alias}

    @property
    def name_to_idx(self) -> Dict[str, int]:
        return {name: self.code2idx(self.name2code(name)) for name in self.classes}

    @property
    def allowed_colors(self) -> List[Tuple[int, int, int]]:
        return [color for colors in self.code2color.values() for color in colors]


FACEPARSE = ClassMapper('FACEPARSE')

if __name__ == '__main__':
    print(len(AVICompMapper.classes))
    AVICompMapper.update_mapper(merge_palette={'Background': ['ViaCircle', 'SurfaceFinish', 'Circuit', 'OpticalPoint']})
    print(len(AVICompMapper.classes))
