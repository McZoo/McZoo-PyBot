import asyncio
import importlib
import os

import utils

session_container = importlib.import_module('session')
session_dict = session_container.session
cfg = utils.Config('./configs/config.yml')
ws_ip = cfg.websockets_ip
stop_file_path = os.path.abspath('./stop.lck')
log_const = importlib.import_module('log')
log_path = log_const.log_path
logger = utils.Logger('WEBSOCKETS', 'debug', log_path)
session = utils.Session(cfg, True, session_dict)
ws = utils.Websockets(ws_ip, session)


async def main():
    plugin_dict = utils.import_plugins('./plugins/', logger)
    while True:
        current_msg = await ws.get_msg()
        for k, i in plugin_dict.items():
            parsed = utils.msg_basic_parser(current_msg)
            utils.thread_call(i, 'websockets_parser', (parsed, logger, session, cfg))


if __name__ == '__main__':
    asyncio.run(main())
