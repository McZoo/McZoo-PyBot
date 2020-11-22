import os
import subprocess

if __name__ == '__main__':
    os.chdir('./mirai-console/')
    mirai_sub_proc = subprocess.Popen(
        ['java', '-cp', './libs/*',
         'net.mamoe.mirai.console.pure.MiraiConsolePureLoader',
         '--no-console'])
    mirai_sub_proc.wait()
