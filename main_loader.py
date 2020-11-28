import importlib
import os
import subprocess
import time

import utils

VERSION_TUPLE: tuple = (0, 0, 1)
VERSION_STR: str = '0.0.1'
REGISTER_NAME = 'Pure Loader'
# TODO: Auto Update
if __name__ == '__main__':
    print('=====PyBot Loader=====')
    try:
        loaded_cores: dict = {}
        cores_const: dict = {}
        cores_list: list = utils.listdir('./cores')
        print(REGISTER_NAME + ' is now version ' + VERSION_STR)
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
            print('Core ' + reg_name + ' is now version ' + ver_str)
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
        time.sleep(20)
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
    except Exception as e:
        print(e)
    finally:
        print('=====Loader Exit=====')
