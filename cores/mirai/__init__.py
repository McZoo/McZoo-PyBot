import os
import re
import subprocess
import sys
import threading
from multiprocessing import shared_memory

import utils

VERSION_TUPLE: tuple = (0, 0, 2)
VERSION_STR: str = '0.0.2'
REGISTRY_NAME: str = 'mirai'


def message_putting_loop(sub_proc: subprocess.Popen, logger_inst: utils.Logger, ok_mem_str: str,
                         enable_output: bool):
    while True:
        origin = sub_proc.stdout.readline()
        line = bytes.decode(origin, encoding='gbk')
        line = re.sub(r'[0-9]*-[0-9]*-[0-9]* [0-9]*:[0-9]*:[0-9]* ', '', line)
        line = re.sub(r'\s$', "", line)
        if re.match(r'I/main: mirai-console started successfully.*', line) is not None:
            ok_mem = shared_memory.SharedMemory(name=ok_mem_str, create=False)
            ok_mem.buf[0] = utils.MemConst.stop()
            ok_mem.close()
        if enable_output:
            if line[0] == 'I':
                logger_inst.log('info', line)
            elif line[0] == 'W':
                logger_inst.log('warning', line)
            elif line[0] == 'E':
                logger_inst.log('error', line)
            else:
                logger_inst.log('debug', line)


def main(log_path: str, ok_mem_str: str, mem_str: str):
    logger = utils.Logger('MIRAI', 'debug', log_path)
    os.chdir('./cores/mirai/mirai-console/')
    mirai_sub_proc = subprocess.Popen(
        ['java', '-cp', './libs/*',
         'net.mamoe.mirai.console.pure.MiraiConsolePureLoader', '--no-console'
         ], stdout=subprocess.PIPE)
    os.chdir('./../../../')
    msg_put_thread = threading.Thread(target=message_putting_loop, args=(mirai_sub_proc, logger, ok_mem_str, True),
                                      daemon=True)
    msg_put_thread.start()
    mem = shared_memory.SharedMemory(name=mem_str, create=False)
    while True:
        if mem.buf[0] == utils.MemConst.stop():
            mirai_sub_proc.terminate()
            logger.log('info', 'Core stopped.')
            sys.exit()
