import os
import re
import platform
from typing import NoReturn
from .misc import is_not_none


class PathFormatter:
    __slots__ = ['_dir']

    WEIGHT_DIRECTORY_STRUCTURE = ['work_dir', 'project', 'target_model', 'update']

    def __init__(self, path=None):
        assert isinstance(path, str), 'Input must be [str]'
        self._dir = path

    @property
    def windows(self) -> str:
        return self._dir.replace('/', '\\')

    @property
    def linux(self) -> str:
        return self._dir.replace('\\', '/')

    @property
    def path(self) -> str:
        return self._dir.replace('\\', os.sep).replace('/', os.sep)

    @staticmethod
    def to_window_format(path: str) -> str:
        assert isinstance(path, str), 'Input must be [str]'
        return path.replace('/', '\\')

    @staticmethod
    def to_linux_format(path: str) -> str:
        assert isinstance(path, str), 'Input must be [str]'
        return path.replace('\\', '/')

    @staticmethod
    def format(path: str) -> str:
        assert isinstance(path, str), 'Input must be [str]'
        if platform.system() != 'Windows':
            path = path.split(':')[-1]
        return path.replace('\\', os.sep).replace('/', os.sep)

    @staticmethod
    def review_dir(path: str, indicator=True) -> NoReturn:
        if indicator:
            print('Linux path:', PathFormatter.to_linux_format(path))
            print('Windows path:', PathFormatter.to_window_format(path))
        else:
            print(PathFormatter.to_linux_format(path))
            print(PathFormatter.to_window_format(path))


class SuffixFormatter:

    ENCRYPT_FORMAT = ['raw', "RAW"]
    SUPPORT_FORMAT = ['png', 'jpg', 'bmp', 'jpeg', 'PNG', 'JPG', 'JPEG', 'BMP', 'mp4', 'MP4', 'mov'] + ENCRYPT_FORMAT
    _support_format = "|".join(SUPPORT_FORMAT)

    REGEX = {
        'ref': re.compile(f'_(?P<suffix>ref).(?P<ext>{_support_format})'),
        'mask': re.compile(f'_(?P<suffix>mask).(?P<ext>{_support_format})'),
        'comp': re.compile(f'_(?P<suffix>comp).(?P<ext>{_support_format})'),
        'id': re.compile(f'_(?P<suffix>id).(?P<ext>{_support_format})'),
        'support_format': re.compile(f'.(?P<ext>{_support_format})')
    }

    MAPPER = {
        'ann': 'Ann',
        'ref': 'Ref',
        'mask': 'Mask',
        'comp': 'Comp',
        'id': 'Id'
    }

    @staticmethod
    def format_suffix(src: str, target: str = 'ref') -> NoReturn:
        clean_root = PathFormatter.format(src)
        for root, _, files in os.walk(clean_root):
            print(f'Working on {root}')
            for file in files:
                SuffixFormatter.format_filename(root, file, target)


    @staticmethod
    def is_file_type(file_name: str, file_type: str) -> bool:
        assert isinstance(file_type, str), f"file_type must be str, while {type(file_type)} is given."
        file_type = file_type.lower()
        if file_type in SuffixFormatter.REGEX.keys():
            search_result = re.search(SuffixFormatter.REGEX['file_type'], file_name)
            if search_result is not None:
                return True
        return False

    @staticmethod
    def get_suffix(file):
        _, ext = os.path.splitext(file)
        suffix_pattern = re.compile('_(?P<suffix>[a-zA-Z]+)' + ext)
        res = re.search(suffix_pattern, file)
        return res['suffix'] if res is not None and res['suffix'] in SuffixFormatter.MAPPER.keys() else None

    @staticmethod
    def is_cur(file: str) -> bool:
        _, ext = os.path.splitext(file)
        suffix_case = '|'.join(SuffixFormatter.MAPPER.keys())
        suffix_pattern = re.compile(rf'_(?P<suffix>{suffix_case})( ?\(\d+\))?' + ext)
        res = re.search(suffix_pattern, file)
        if res is not None or ext[1:] not in SuffixFormatter.SUPPORT_FORMAT:
            return False
        return True

    @staticmethod
    def is_attr(file: str, attr: str) -> bool:
        attr = attr.lower()
        if attr in ['cur']:
            return SuffixFormatter.is_cur(file)

        suffix_pattern = SuffixFormatter.REGEX[attr]
        res = re.search(suffix_pattern, file)
        return is_not_none(res)

    @staticmethod
    def is_encrypted_format(file: str) -> bool:
        return file.endswith(tuple(SuffixFormatter.ENCRYPT_FORMAT))

    @staticmethod
    def is_supported_format(file: str) -> bool:
        res = re.search(SuffixFormatter.REGEX['support_format'], file)
        return is_not_none(res) and file.endswith(res['ext'])

    @staticmethod
    def separate_by_suffix(work_dir, inplace=True):
        from ..data.image import SingleImage
        work_dir = PathFormatter.format(work_dir)
        files = os.listdir(work_dir)
        for file in files:
            file_path = os.path.join(work_dir, file)
            if os.path.isfile(file_path):
                target_folder = None
                if SuffixFormatter.is_cur(file_path):
                    target_folder = 'Cur'
                else:
                    suffix = SuffixFormatter.get_suffix(file_path)
                    if suffix in SuffixFormatter.MAPPER.keys():
                        target_folder = SuffixFormatter.MAPPER[suffix]
                if target_folder is not None and target_folder not in work_dir:
                    img = SingleImage(file_path)
                    img.copy_to(os.path.join(work_dir, target_folder), force=True)
                    if inplace:
                        os.remove(file_path)

    @staticmethod
    def move_by_type(root: str, log=True):
        root = PathFormatter.format(root)
        for work_dir, _, _ in os.walk(root):
            if log:
                print('> Working on:', work_dir)
            SuffixFormatter.separate_by_suffix(work_dir)

def service_info(service: str) -> str:
    """Get service information.

    Args:
        service (str): Service name.

    Returns:
        str: Service information.
    """
    return f"<{'Service':^7}> {service:=^40}"


def phase_info(phase: str) -> str:
    """Get phase information.

    Args:
        phase (str): Phase name.

    Returns:
        str: Phase information.
    """
    return f"<{'Phase':^7}> {phase:-^40}"


def stage_info(stage: str) -> str:
    """Get stage information.

    Args:
        stage (str): Stage name.

    Returns:
        str: Stage information.
    """
    return f"<{'Stage':^7}> {stage}"

if __name__ == '__main__':
    print(SuffixFormatter.is_supported_format('.jpg.x'))
    print(os.path.splitext('_gerb.bmp'))
    print('.mbp'[1:])

