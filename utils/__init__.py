import importlib
import json
import logging
import os
import threading

import requests
import websockets
from ruamel import yaml as yaml


class Config:
    def __init__(self, configs_path: str):
        """
        Automatically loads yaml config
        """
        yaml_fs = open(os.path.abspath(configs_path), "r")
        self.config_dict = yaml.load(yaml_fs, Loader=yaml.Loader)
        self.httpip = self.config_dict['HttpIP']
        self.websockets_ip = self.config_dict['Websockets_IP']
        yaml_fs.close()


class Session:
    def __init__(self, config_inst: Config):
        """
        Automatically generates session
        """
        self.config = config_inst
        self.session_dict = self.gen()
        self.session_key = self.session_dict['sessionKey']
        self.qq = self.session_dict['qq']

    def gen(self):
        """
                Generate & verify a Mirai Session
                return format:
                {
                'sessionKey': 'ExampleString',
                'qq': 1234567890
                }
                """

        reply = requests.post(self.config.httpip + '/auth',
                              data=json.dumps({"authKey": self.config.config_dict['authKey']}))
        reply_dict = json.loads(reply.text)
        session = {"sessionKey": reply_dict['session'], "qq": self.config.config_dict['qq']}
        requests.post(self.config.httpip + '/verify', data=json.dumps(session))
        return session  # return session and qq in dict form

    def release(self):
        """
                release a Mirai Session
                :return: nothing
                """
        requests.post(self.config.httpip + '/release', data=json.dumps(self.session_dict))


class Websockets:
    def __init__(self, mirai_inst, session):
        self.session = session
        self.mirai_inst = mirai_inst

    async def get_msg(self):
        url = self.mirai_inst.websockets_ip + '/all?sessionKey=' + self.session.session_key
        with websockets.connect(url) as current_ws_conn:
            message_dict = json.loads(await current_ws_conn.recv())
        return message_dict

    async def get_msg_cycle(self, confirm: bool):
        while confirm:
            cur_msg = await self.get_msg()
            print(cur_msg)  # TODO


def send_dict(config_inst: Config, session: dict, target: int, content: dict, target_type: str = 'group'):
    """
    Send a dict-wrapped message to a friend/group
    returns message id if success , else -1
    :param config_inst: Config instance
    :param session: dict from Mirai.gen_session()
    :param target: int
    :param content: dict
    :param target_type: 'friend' or 'group'
    :return:
    """
    message_dict = {
        'sessionKey': session['session'],
        'target': target,
        'messageChain': [
            content
        ]
    }
    if target_type == 'friend':
        extra_url = '/sendFriendMessage'
    else:
        extra_url = '/sendGroupMessage'
    url = config_inst.httpip + extra_url
    send_data = json.dumps(message_dict)
    reply = requests.post(url, send_data)
    msg_id = -1
    try:
        reply_dict = json.loads(reply.text)
        msg_id = reply_dict['messageId']
    finally:
        return msg_id


class Threader:
    def __init__(self):
        self.pool: list = []

    def thread_call(self, command: str):
        split_comm: list = command.split('(', 1)
        func_full: str = split_comm[0]
        params_str: str = str.rstrip(split_comm[1], ')')
        params: list = params_str.split(',')
        func_list: list = func_full.rsplit('.', 2)
        if len(func_list) >= 3:
            package: str = func_list[2]
        else:
            package: str = ''
        if len(func_list) >= 2:
            module: str = func_list[1]
        else:
            module: str = 'builtins'
        func: str = func_list[0]
        imported_module = importlib.import_module(module, package)
        target_func = getattr(imported_module, func)
        gen_thread = threading.Thread(target=target_func, args=params, daemon=True)
        self.pool.append(gen_thread)
        gen_thread.start()


def listdir(path: str):
    """
    An implementation of os.listdir() , removes python related files & dirs
    :param path: string
    :return: list
    """
    origin: list = os.listdir(path)
    if '__init__.py' in origin:
        origin.remove('__init__.py')
    if '__pycache__' in origin:
        origin.remove('__pycache__')
    return origin


class Logger:
    """
    Implementation & wrapping of logging
    """
    def __init__(self, name: str, lvl: str, file_path: str):
        self.logger_inst = logging.Logger(name)
        self.stream_handler = logging.StreamHandler()
        self.file_handler = logging.FileHandler(file_path)
        self.formatter = logging.Formatter('[%(name)s] [%(asctime)s] [%(levelname)s] %(message)s')
        if lvl == 'DEBUG':
            self.logger_inst.setLevel(logging.DEBUG)
            self.stream_handler.setLevel(logging.DEBUG)
            self.file_handler.setLevel(logging.DEBUG)
        if lvl == 'INFO':
            self.logger_inst.setLevel(logging.INFO)
            self.stream_handler.setLevel(logging.INFO)
            self.file_handler.setLevel(logging.INFO)
        if lvl == 'WARNING':
            self.logger_inst.setLevel(logging.WARNING)
            self.stream_handler.setLevel(logging.WARNING)
            self.file_handler.setLevel(logging.WARNING)
        if lvl == 'ERROR':
            self.logger_inst.setLevel(logging.ERROR)
            self.stream_handler.setLevel(logging.ERROR)
            self.file_handler.setLevel(logging.ERROR)
        if lvl == 'CRITICAL':
            self.logger_inst.setLevel(logging.CRITICAL)
            self.stream_handler.setLevel(logging.CRITICAL)
            self.file_handler.setLevel(logging.CRITICAL)
        self.stream_handler.setFormatter(self.formatter)
        self.file_handler.setFormatter(self.formatter)
        self.logger_inst.addHandler(self.stream_handler)
        self.logger_inst.addHandler(self.file_handler)
