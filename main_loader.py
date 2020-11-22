import importlib
import os
import subprocess

import utils

VERSION_TUPLE: tuple = (0, 0, 1)
VERSION_STR: str = '0.0.1'

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
    print('=====Program Exit=====')
