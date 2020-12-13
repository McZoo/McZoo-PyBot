import importlib
import multiprocessing
import sys
import threading
import time
from multiprocessing import shared_memory

import utils

VERSION_TUPLE: tuple = (0, 0, 1)
VERSION_STR: str = '0.0.1'
REGISTRY_NAME = 'Pure Loader'
LOG_LEVEL = 'debug'


# TODO: Auto Update

def input_parser(mem_name: str):
    mem = shared_memory.SharedMemory(name=mem_name, create=False)
    while True:
        input_str = input()
        if input_str == 'stop':
            mem.buf[0] = utils.MemConst.stop()
        return


if __name__ == '__main__':
    exec_time = time.strftime('%Y-%m-%d %H_%M_%S', time.localtime(time.time()))
    log_path = './logs/{0}.log'.format(exec_time)
    logger = utils.Logger('LOADER', LOG_LEVEL, log_path)
    logger.log('info', '=====PyBot Loader=====')
    try:
        loaded_cores: dict[str: multiprocessing.Process] = {}
        cores: dict[str: object] = {}
        cores_list: list[str] = utils.listdir('./cores')
        logger.log('info', REGISTRY_NAME + ' is now version ' + VERSION_STR)
        for u in cores_list:
            '''
            Load cores
            '''
            module = importlib.import_module('cores.' + u)
            cores[u] = module
            if VERSION_TUPLE[0] != module.VERSION_TUPLE[0]:
                raise utils.VersionError('Incompatible Core')
            ver_str = module.VERSION_STR
            reg_name = module.REGISTRY_NAME
            logger.log('info', 'Core ' + reg_name + ' is now version ' + ver_str)
        cfg = utils.Config('configs/config.yml')
        # Mirai Starter
        mirai_ok_mem = shared_memory.SharedMemory(name='mirai_ok', create=True, size=1)
        mirai_ok_mem.buf[0] = utils.MemConst.init()
        stage = 1
        msg_memory = shared_memory.SharedMemory(name='msg_mem', create=True, size=1)
        msg_memory.buf[0] = utils.MemConst.init()
        if 'mirai' not in cores_list:
            raise ModuleNotFoundError('Mirai is a necessary core')
        else:
            loaded_cores['mirai'] = multiprocessing.Process(target=cores['mirai'].main,
                                                            args=(log_path, 'mirai_ok', 'msg_mem'))
            loaded_cores['mirai'].start()
        while mirai_ok_mem.buf[0] != utils.MemConst.stop():
            pass
        mirai_ok_mem.close()
        mirai_ok_mem.unlink()
        # Mirai Starter End
        # Create session
        session = utils.Session(cfg)
        for u in cores_list:
            '''
            Start every core
            '''
            if u == 'mirai':
                continue
            loaded_cores[u] = multiprocessing.Process(target=cores[u].main,
                                                      args=(log_path, session, cfg, 'msg_mem'))
            loaded_cores[u].start()
        stop_mem = shared_memory.SharedMemory(name='stop_mem', create=True, size=1)
        stop_mem.buf[0] = utils.MemConst.init()
        input_thread = threading.Thread(target=input_parser, args=('stop_mem',))
        input_thread.start()
        while True:
            if stop_mem.buf[0] == utils.MemConst.stop():
                stop_mem.close()
                stop_mem.unlink()
                msg_memory.buf[0] = utils.MemConst.stop()
                time.sleep(1)
                msg_memory.close()
                msg_memory.unlink()
                logger.log('info', '=====Loader Exit=====')
                break
    except Exception as e:
        logger.stacktrace(e, 'error')
    finally:
        sys.exit()
