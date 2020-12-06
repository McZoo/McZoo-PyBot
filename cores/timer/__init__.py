import multiprocessing

import utils

VERSION_TUPLE: tuple = (0, 0, 0)
VERSION_STR: str = '0.0.0'
REGISTRY_NAME: str = 'timer'


def main(log_path: str, session: utils.Session, cfg: utils.Config, stop_queue: multiprocessing.Queue):
    if log_path:
        if session:
            if cfg:
                if stop_queue:
                    pass
