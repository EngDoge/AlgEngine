from multiprocessing import Pool
from functools import partial
from typing import Callable, Optional, Iterable

from tqdm import tqdm

def parallel_run(func: Callable,
                 data: Iterable,
                 num_workers: int = 6,
                 time_out: Optional[int] = None,
                 with_return: bool = False,
                 **kwargs) -> dict | None:
        """
        The original synchronized function should be defined as:
        >>> def func(item, *args, **kwargs):
                pass

        """

        result = dict()
        kwargs = dict() if kwargs is None else kwargs
        total_num = len(data)
        pbar = tqdm(total=total_num)

        def callback(*args):
            pbar.update()
        
        with Pool(num_workers) as pool:
            apply_fn = partial(func, **kwargs)
            res = [pool.apply_async(func=apply_fn,
                                    args=(item,),
                                    callback=callback) for item in data]
            result = {item: future.get(timeout=time_out) for item, future in zip(data, res)}
        if with_return:
            return result