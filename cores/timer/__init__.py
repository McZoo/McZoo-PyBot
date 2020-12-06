import multiprocessing
import threading
import time

import utils

VERSION_TUPLE: tuple = (0, 0, 0)
VERSION_STR: str = '0.0.0'
REGISTRY_NAME: str = 'timer'


def main(log_path: str, session: utils.Session, cfg: utils.Config, stop_queue: multiprocessing.Queue):
    if log_path:
        pass
    shut = threading.Thread(target=utils.shut_monitor, args=(stop_queue,))
    shut.start()
    while True:
        cur_time: tuple = time.localtime(time.time())
        if cur_time[4] % 5 == 0:
            reply_list = [{
                "type": "Plain",
                "text": "现在是" + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}
            ]
            for u in cfg.config_dict['group']:
                utils.send_list(cfg, session.session_dict, u, reply_list, 'group')
        time.sleep(60)
