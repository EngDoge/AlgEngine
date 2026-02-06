import re
from typing import Optional, Union


def parse_device_id(device: Union[str, int]) -> Optional[int]:
    """Parse device index from a string.

    Args:
        device (str): The typical style of string specifying device,
            e.g.: 'cuda:0', 'cpu'.

    Returns:
        Optional[int]: The return value depends on the type of device.
            If device is 'cuda': cuda device index, defaults to `0`.
            If device is 'cpu': `-1`.
            Otherwise, `None` will be returned.
    """
    if isinstance(device, int):
        return device
    if device.isdigit():
        return int(device)
    if device == 'cpu':
        return -1
    if 'cuda' in device:
        return parse_cuda_device_id(device)
    return None

DEVICE_ID_PATTERN = re.compile(r"cuda\s?:\s?([0-9]+)")

def parse_cuda_device_id(device: str) -> int:
    """Parse cuda device index from a string.

    Args:
        device (str): The typical style of string specifying cuda device,
            e.g.: 'cuda:0'.

    Returns:
        int: The parsed device id, defaults to `0`.
    """
    if device == 'cuda':
        return 0
    device_id = DEVICE_ID_PATTERN.search(device)
    if device_id:
        return int(device_id.group(1))
    raise ValueError(f"Invalid cuda device id: {device}")

if __name__ == "__main__":
    print(parse_cuda_device_id("cuda:"))