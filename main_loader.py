import importlib
import multiprocessing
import os
import sys
import time
import subprocess
import utils

VERSION_TUPLE: tuple = (0, 0, 1)
VERSION_STR: str = '0.0.1'
REGISTRY_NAME = 'Pure Loader'
LOG_LEVEL = 'debug'
# TODO: Auto Update
if __name__ == '__main__':
    exec_time = time.strftime('%Y-%m-%d %H_%M_%S', time.localtime(time.time()))
    log_path = './logs/' + exec_time + '.log'
    logger = utils.Logger('LOADER', LOG_LEVEL, log_path)
    logger.log('info', '=====PyBot Loader=====')
    try:
        loaded_cores: dict = {}
        cores: dict = {}
        cores_list: list = utils.listdir('./cores')
        logger.log('info', REGISTRY_NAME + ' is now version ' + VERSION_STR)
        for u in cores_list:
            '''
            Load cores
            '''
            module = importlib.import_module('cores.' + u)
            cores[u] = module
            if VERSION_TUPLE[0] != module.VERSION_TUPLE[0]:
                raise ModuleNotFoundError('Incompatible Core')
            ver_str = module.VERSION_STR
            reg_name = module.REGISTRY_NAME
            logger.log('info', 'Core ' + reg_name + ' is now version ' + ver_str)
        cfg = utils.Config('configs/config.yml')
        stop_queues: dict = {}
        # Mirai Starter
        mirai_ok_queue = multiprocessing.Queue()
        stop_queues['mirai'] = multiprocessing.Queue()
        if 'mirai' not in cores_list:
            raise ModuleNotFoundError('Mirai is a necessary core')
        else:
            loaded_cores['mirai'] = multiprocessing.Process(target=cores['mirai'].main,
                                                            args=(log_path, mirai_ok_queue, stop_queues['mirai']))
            loaded_cores['mirai'].start()
        # Mirai Starter End
        mirai_ok_queue.get(block=True)
        # Create session
        session = utils.Session(cfg)
        if not os.path.exists('./input_parser.py'):
            raise ModuleNotFoundError('Input parser not found, stop program!')
        for u in cores_list:
            '''
            Start every core
            '''
            if u == 'mirai':
                continue
            stop_queues[u] = multiprocessing.Queue()
            loaded_cores[u] = multiprocessing.Process(target=cores[u].main,
                                                      args=(log_path, session, cfg, stop_queues[u]))
            loaded_cores[u].start()
        subprocess.Popen(args=['python', './input_parser.py'])
        while True:
            if os.path.exists('./stop.lck'):
                for u in loaded_cores.keys():
                    if u == 'mirai':
                        continue
                    try:
                        stop_msg = stop_queues[u].put('STOP')
                    finally:
                        pass
                stop_queues['mirai'].put('STOP')
                os.remove('./stop.lck')
                logger.log('info', '=====Loader Exit=====')
                break
    except Exception as e:
        logger.stacktrace(e, 'error')
    finally:
        sys.exit()