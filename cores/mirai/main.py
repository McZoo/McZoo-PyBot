import importlib
import os
import subprocess
import sys
import threading
import time
import re

import utils


def message_putting_loop(sub_proc: subprocess.Popen, logger_inst: utils.Logger):
    while True:
        line = bytes.decode(sub_proc.stdout.readline(), encoding='gbk')
        if re.match(r'.*I/main: mirai-console started successfully.*', line) is not None:
            ok_file_path = os.path.abspath('./mirai_ok.lck')
            ok_fs = open(ok_file_path, 'w')
            ok_fs.close()
        logger_inst.log('debug', line)


if __name__ == '__main__':
    stop_file_path = os.path.abspath('./stop.lck')
    log_const = importlib.import_module('log')
    log_path = log_const.log_path
    logger = utils.Logger('MIRAI', 'debug', log_path)
    os.chdir('./cores/mirai/mirai-console/')
    mirai_sub_proc = subprocess.Popen(
        ['java', '-cp', './libs/*',
         'net.mamoe.mirai.console.pure.MiraiConsolePureLoader',
         '--no-console'], stdout=subprocess.PIPE)
    os.chdir('./../../../')
    msg_put_thread = threading.Thread(target=message_putting_loop, args=(mirai_sub_proc, logger), daemon=True)
    msg_put_thread.start()
    while True:
        if os.path.exists(stop_file_path):
            mirai_sub_proc.terminate()
            logger.log('info', '[Mirai Core]Core terminated.')
            if os.path.exists('./mirai_ok.lck'):
                os.remove('./mirai_ok.lck')
            sys.exit()
        time.sleep(0.001)
