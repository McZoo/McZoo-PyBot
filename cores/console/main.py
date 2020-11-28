import importlib
import os
import sys
import time

import utils

if __name__ == '__main__':
    log_const = importlib.import_module('log')
    log_path = log_const.log_path
    logger = utils.Logger('CONSOLE', 'debug', log_path)
    if os.path.exists('./stop.lck'):
        os.remove('./stop.lck')
    while True:
        input_str = input()
        if input_str == 'stop':
            logger.log('info', 'Stopping PyBot...')
            stop_file_path = os.path.abspath('./stop.lck')
            stop_fs = open(stop_file_path, 'w')
            stop_fs.close()
            time.sleep(0.5)
            os.remove(stop_file_path)
            sys.exit()
