import asyncio
import sys
import threading
from multiprocessing import shared_memory

import utils

VERSION_TUPLE: tuple = (0, 0, 1)
VERSION_STR: str = '0.0.1'
REGISTRY_NAME: str = 'websockets'


def main(log_path: str, session: utils.Session, cfg: utils.Config, mem_str: str):
    ws_ip = cfg.websockets_ip
    ws = utils.Websockets(ws_ip, session)
    logger = utils.Logger('WEBSOCKETS', 'debug', log_path)
    plugin_dict = utils.import_plugins('./plugins/', logger)
    parser = threading.Thread(target=parse, args=(plugin_dict, ws, session, cfg, logger))
    parser.start()
    mem = shared_memory.SharedMemory(name=mem_str, create=False)
    while True:
        if mem == utils.MemConst.stop():
            logger.log('info', 'Core stopped.')
            sys.exit()


def parse(plugin_dict, ws: utils.Websockets, session: utils.Session, cfg: utils.Config, logger: utils.Logger):
    while True:
        current_msg = asyncio.run(ws.get_msg())
        for k, i in plugin_dict.items():
            parsed = utils.msg_basic_parser(current_msg)
            utils.thread_call(i, 'websockets_parser', (parsed, logger, session, cfg))
