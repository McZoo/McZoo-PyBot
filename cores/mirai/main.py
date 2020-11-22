import os
import subprocess
import sys
import time

if __name__ == '__main__':
    os.chdir('./cores/mirai/mirai-console/')
    mirai_sub_proc = subprocess.Popen(
        ['java', '-cp', './libs/*',
         'net.mamoe.mirai.console.pure.MiraiConsolePureLoader',
         '--no-console'])
    os.chdir('./../../../')
    stop_file_path = os.path.abspath('./stop.lck')
    while True:
        if os.path.exists(stop_file_path):
            mirai_sub_proc.terminate()
            print('[Mirai Core]Core terminated.')
            sys.exit()
        time.sleep(0.001)
