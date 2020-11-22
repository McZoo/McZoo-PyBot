import os

import subprocess
import typing

import utils
cores: typing.Iterator[tuple[str, list[str], list[str]]] = os.walk('./cores', topdown=True)
loaded_cores: dict = {}
cores_const: dict = {}
for entry in cores:
    if entry[0] == './cores':
        cores_list: list = entry[1]
        for u in cores_list:
            exec_path = './cores/' + u + '/main.py'
            command = ['python ', os.path.abspath(exec_path)]
            executing = subprocess.Popen(command)
            loaded_cores[u] = executing
    else:
        pass
