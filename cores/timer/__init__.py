from multiprocessing import shared_memory
import sys
import threading
import time

import utils

VERSION_TUPLE: tuple = (0, 0, 0)
VERSION_STR: str = '0.0.0'
REGISTRY_NAME: str = 'timer'


def main(log_path: str, session: utils.Session, cfg: utils.Config, mem_str: str):
    logger = utils.Logger('TIMER', 'debug', log_path)
    logger.log('info', 'Started core.')
    parser = threading.Thread(target=parse, args=(cfg, session))
    parser.start()
    mem = shared_memory.SharedMemory(name=mem_str, create=False)
    while True:
        time.sleep(0.01)
        if mem == utils.MemConst.stop():
            logger.log('info', 'Core stopped.')
            sys.exit()


def parse(cfg: utils.Config, session: utils.Session):
    while True:
        cur_time: tuple = time.localtime(time.time())
        if cur_time[4] % 10 == 0 and cur_time[5] == 0:
            reply_list = [{
                "type": "Plain",
                "text": "现在是 {0}".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))}
            ]
            for u in cfg.config_dict['group']:
                utils.send_list(cfg, session.session_dict, u, reply_list, 'group')
        time.sleep(1)
