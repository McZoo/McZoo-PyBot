import asyncio
import multiprocessing
import threading

import utils

VERSION_TUPLE: tuple = (0, 0, 1)
VERSION_STR: str = '0.0.1'
REGISTRY_NAME: str = 'websockets'


def main(log_path: str, session: utils.Session, cfg: utils.Config, stop_queue: multiprocessing.Queue):
    ws_ip = cfg.websockets_ip
    ws = utils.Websockets(ws_ip, session)
    logger = utils.Logger('WEBSOCKETS', 'debug', log_path)
    plugin_dict = utils.import_plugins('./plugins/', logger)
    shut = threading.Thread(target=utils.shut_monitor, args=(stop_queue,))
    shut.start()
    asyncio.run(parse(plugin_dict, ws, session, cfg, logger))


async def parse(plugin_dict, ws: utils.Websockets, session: utils.Session, cfg: utils.Config, logger: utils.Logger):
    while True:
        current_msg = await ws.get_msg()
        for k, i in plugin_dict.items():
            parsed = utils.msg_basic_parser(current_msg)
            utils.thread_call(i, 'websockets_parser', (parsed, logger, session, cfg))
