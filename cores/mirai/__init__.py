import multiprocessing
import os
import re
import subprocess
import sys
import threading

import utils

VERSION_TUPLE: tuple = (0, 0, 2)
VERSION_STR: str = '0.0.2'
REGISTRY_NAME: str = 'mirai'


def message_putting_loop(sub_proc: subprocess.Popen, logger_inst: utils.Logger, ok_queue: multiprocessing.Queue,
                         enable_output: bool):
    while True:
        origin = sub_proc.stdout.readline()
        line = bytes.decode(origin, encoding='gbk')
        line = re.sub(r'[0-9]*-[0-9]*-[0-9]* [0-9]*:[0-9]*:[0-9]* ', '', line)
        line = re.sub(r'\s$', "", line)
        if re.match(r'I/main: mirai-console started successfully.*', line) is not None:
            ok_queue.put('MIRAI OK')
        if enable_output:
            if line[0] == 'I':
                logger_inst.log('info', line)
            elif line[0] == 'W':
                logger_inst.log('warning', line)
            elif line[0] == 'E':
                logger_inst.log('error', line)
            else:
                logger_inst.log('debug', line)


def main(log_path: str, ok_queue: multiprocessing.Queue, stop_queue: multiprocessing.Queue):
    logger = utils.Logger('MIRAI', 'debug', log_path)
    os.chdir('./cores/mirai/mirai-console/')
    mirai_sub_proc = subprocess.Popen(
        ['java', '-cp', './libs/*',
         'net.mamoe.mirai.console.pure.MiraiConsolePureLoader', '--no-console'
         ], stdout=subprocess.PIPE)
    os.chdir('./../../../')
    msg_put_thread = threading.Thread(target=message_putting_loop, args=(mirai_sub_proc, logger, ok_queue, True),
                                      daemon=True)
    msg_put_thread.start()
    while True:
        item = stop_queue.get(block=True)
        if item == 'STOP':
            mirai_sub_proc.terminate()
            sys.exit()
