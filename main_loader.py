import importlib
import os
import subprocess
import time

import utils

VERSION_TUPLE: tuple = (0, 0, 1)
VERSION_STR: str = '0.0.1'
# TODO: Auto Update
if __name__ == '__main__':
    loaded_cores: dict = {}
    cores_const: dict = {}
    cores_list: list = utils.listdir('./cores')
    print('=====PyBot Loader=====')
    print('Loader is now version ' + VERSION_STR)
    for u in cores_list:
        '''
        Load cores
        '''
        tmp_module = importlib.import_module('cores.' + u + '.const')
        cores_const[u] = tmp_module
        tmp_ver = tmp_module.VERSION_STR
        print('Core ' + u + ' is now version ' + tmp_ver)
    cfg = utils.Config('./configs/loader_config.yml')
    for u in cores_list:
        '''
        Start every core
        '''
        exec_path = './cores/' + u + '/main.py'
        command = ['python ', os.path.abspath(exec_path)]
        executing = subprocess.Popen(command)
        loaded_cores[u] = executing
    time.sleep(20)
    session = utils.Session(cfg)
    session_fs = open('./session.py', 'w')
    session_dict_str: str = str(session.session_dict)
    session_content: list = ['session: dict = ' + session_dict_str, '']
    session_fs.writelines(session_content)
    session_fs.close()
    for u in loaded_cores.keys():
        '''
        Wait until every core is dead
        '''
        loaded_cores[u].wait()
    if os.path.exists('./session.py'):
        os.remove('./session.py')
    print('=====Program Exit=====')
