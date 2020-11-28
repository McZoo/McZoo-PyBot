import importlib
import os
import subprocess
import time

import utils

VERSION_TUPLE: tuple = (0, 0, 1)
VERSION_STR: str = '0.0.1'
REGISTER_NAME = 'Pure Loader'
LOG_LEVEL = 'debug'
# TODO: Auto Update
if __name__ == '__main__':
    exec_time = time.strftime('%Y-%m-%d %H_%M_%S', time.localtime(time.time()))
    log_path = './logs/' + exec_time + '.log'
    logger = utils.Logger('LOADER', LOG_LEVEL, log_path)
    logger.log('info', '=====PyBot Loader=====')
    try:
        # Create log share
        log_fs = open('./log.py', 'w')
        log_content: list = ['log_path: str = \'' + log_path + '\'', '']
        log_fs.writelines(log_content)
        log_fs.close()
        # Create log share end
        loaded_cores: dict = {}
        cores_const: dict = {}
        cores_list: list = utils.listdir('./cores')
        logger.log('info', REGISTER_NAME + ' is now version ' + VERSION_STR)
        for u in cores_list:
            '''
            Load cores
            '''
            module = importlib.import_module('cores.' + u)
            cores_const[u] = module
            if VERSION_TUPLE[0] != module.VERSION_TUPLE[0]:
                raise ModuleNotFoundError('Incompatible Core')
            ver_str = module.VERSION_STR
            reg_name = module.REGISTER_NAME
            logger.log('info', 'Core ' + reg_name + ' is now version ' + ver_str)
        cfg = utils.Config('./configs/loader_config.yml')
        # Mirai Starter
        if 'mirai' not in cores_list:
            raise ModuleNotFoundError('Mirai is a necessary core')
        else:
            exec_path = './cores/mirai/main.py'
            command = ['python ', os.path.abspath(exec_path)]
            executing = subprocess.Popen(command)
            loaded_cores['mirai'] = executing
            cores_list.remove('mirai')
        # Mirai Starter End
        while os.path.exists('./mirai_ok.lck') is False:
            pass
        # Create session
        session = utils.Session(cfg)
        session_fs = open('./session.py', 'w')
        session_dict_str: str = str(session.session_dict)
        session_content: list = ['session: dict = ' + session_dict_str, '']
        session_fs.writelines(session_content)
        session_fs.close()
        # Create session end
        for u in cores_list:
            '''
            Start every core
            '''
            exec_path = './cores/' + u + '/main.py'
            command = ['python ', os.path.abspath(exec_path)]
            executing = subprocess.Popen(command)
            loaded_cores[u] = executing
        for u in loaded_cores.keys():
            '''
            Wait until every core is dead
            '''
            loaded_cores[u].wait()
        if os.path.exists('./session.py'):
            os.remove('./session.py')
        if os.path.exists('./log.py'):
            os.remove('./log.py')
    except Exception as e:
        logger.stacktrace(e, 'error')
    finally:
        logger.log('info', '=====Loader Exit=====')
