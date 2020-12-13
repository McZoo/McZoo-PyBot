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
        self.httpip = 'http://{0}:{1}'.format(self.config_dict['IP'], self.config_dict['Port'])
        self.websockets_ip = 'ws://{0}:{1}'.format(self.config_dict['IP'], self.config_dict['Port'])
        yaml_fs.close()


class Session:
    def __init__(self, config_inst: Config, restore=False, session_dict=None):
        """
        Automatically generates session
        """
        self.config = config_inst
        if not restore:
            self.session_dict = self.gen()
        else:
            self.session_dict = session_dict
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
    def __init__(self, ws_ip, session):
        self.session = session
        self.ws_ip = ws_ip

    async def get_msg(self):
        url = self.ws_ip + '/message?sessionKey=' + self.session.session_key
        async with websockets.connect(url) as current_ws_conn:
            message_dict = json.loads(await current_ws_conn.recv())
        return message_dict

    async def print_msg_cycle(self, confirm: bool):
        while confirm:
            cur_msg = await self.get_msg()
            print(cur_msg)


class Threader:
    def __init__(self):
        self.pool: list = []

    def command_call(self, command: str):
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


class VersionError(Exception):
    def __init__(self, *args, **kwargs):
        pass


class MemConst:
    """
    The class of memory consts.One byte.To be used as flags in shared memory.
    """

    @staticmethod
    def stop():
        return 255

    @staticmethod
    def init():
        return 0


class Logger:
    """
    Implementation & wrapping of logging
    """

    def __init__(self, name: str, basic_lvl: str, file_path: str):
        """

        :param name: string, name of the logger
        :param basic_lvl: string, one of 'debug','info','warning','error','critical'
        :param file_path: string, the path of log saving path
        """
        self.logger_inst = logging.Logger(name)
        self.stream_handler = logging.StreamHandler()
        self.file_handler = logging.FileHandler(file_path)
        self.formatter = logging.Formatter('[%(name)s] [%(asctime)s] [%(levelname)s] %(message)s')
        if basic_lvl == 'debug':
            self.logger_inst.setLevel(logging.DEBUG)
            self.stream_handler.setLevel(logging.DEBUG)
            self.file_handler.setLevel(logging.DEBUG)
        if basic_lvl == 'info':
            self.logger_inst.setLevel(logging.INFO)
            self.stream_handler.setLevel(logging.INFO)
            self.file_handler.setLevel(logging.INFO)
        if basic_lvl == 'warning':
            self.logger_inst.setLevel(logging.WARNING)
            self.stream_handler.setLevel(logging.WARNING)
            self.file_handler.setLevel(logging.WARNING)
        if basic_lvl == 'error':
            self.logger_inst.setLevel(logging.ERROR)
            self.stream_handler.setLevel(logging.ERROR)
            self.file_handler.setLevel(logging.ERROR)
        if basic_lvl == 'critical':
            self.logger_inst.setLevel(logging.CRITICAL)
            self.stream_handler.setLevel(logging.CRITICAL)
            self.file_handler.setLevel(logging.CRITICAL)
        self.stream_handler.setFormatter(self.formatter)
        self.file_handler.setFormatter(self.formatter)
        self.logger_inst.addHandler(self.stream_handler)
        self.logger_inst.addHandler(self.file_handler)

    def log(self, lvl: str, message: str) -> None:
        """
        :param lvl: 'debug'/'info'/'warning'/'error'/'critical'
        :param message:
        """
        if lvl == 'debug':
            self.logger_inst.debug(message)
        if lvl == 'info':
            self.logger_inst.info(message)
        if lvl == 'warning':
            self.logger_inst.warning(message)
        if lvl == 'error':
            self.logger_inst.error(message)
        if lvl == 'critical':
            self.logger_inst.critical(message)

    def stacktrace(self, exception: Exception, lvl: str):
        self.logger_inst.exception(exception)
        if lvl == 'debug':
            self.logger_inst.debug(exception, exc_info=True)
        if lvl == 'info':
            self.logger_inst.info(exception, exc_info=True)
        if lvl == 'warning':
            self.logger_inst.warning(exception, exc_info=True)
        if lvl == 'error':
            self.logger_inst.error(exception, exc_info=True)
        if lvl == 'critical':
            self.logger_inst.critical(exception, exc_info=True)


def listdir(path: str, remove_suffix: bool = False):
    """
    An implementation of os.listdir() , removes python related files & dirs
    :param remove_suffix: bool
    :param path: string
    :return: list
    """
    origin: list = os.listdir(path)
    if '__init__.py' in origin:
        origin.remove('__init__.py')
    if '__pycache__' in origin:
        origin.remove('__pycache__')
    if not remove_suffix:
        return origin
    else:
        new = []
        for i in origin:
            new.append(os.path.splitext(i)[0])
        return new


def import_plugins(plugin_folder_path: str, logger: Logger):
    plugin_dict = {}
    entries: list[str] = listdir(plugin_folder_path, True)
    for i in entries:
        tmp_mod = importlib.import_module('plugins.' + i)
        if plugin_dict.get(tmp_mod.REGISTRY_NAME) is not None:
            raise AttributeError('Duplicated plugin')
        else:
            plugin_dict[tmp_mod.REGISTRY_NAME] = tmp_mod
    logger.log('info', 'Loaded ' + str(len(plugin_dict)) + ' plugin(s).')
    return plugin_dict


def send_list(config_inst: Config, session: dict, target: int, content: list, target_type: str = 'group'):
    """
    Send a dict-wrapped message to a friend/group
    returns message id if success , else -1
    :param config_inst: Config instance
    :param session: dict from Mirai.gen_session()
    :param target: int
    :param content: list
    :param target_type: 'friend' or 'group'
    :return:
    """
    message_dict = {
        'sessionKey': session['sessionKey'],
        'target': target,
        'messageChain': content
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


def thread_call(module: object, func: str, param: list or tuple):
    target_func = getattr(module, func)
    gen_thread = threading.Thread(target=target_func, args=param, daemon=True)
    gen_thread.start()


def msg_basic_parser(msg_dict: dict):
    """
    :return:
    {
        'sender_id': int
        'msg_id': int
        (optional) 'plain': list[str]
        (optional) 'at': list[int]
    }
    """
    if msg_dict['type'] == 'GroupMessage':
        returning: dict = {}
        msg: list = msg_dict['messageChain']
        sender = msg_dict['sender']
        sender_id = sender['id']
        returning['group_id'] = sender['group']['id']
        returning['sender_id'] = sender_id
        plain_list: list = []
        at_list: list = []
        for dicts in msg:
            if dicts['type'] == 'Source':
                returning['msg_id'] = dicts['id']
            if dicts['type'] == 'Plain':
                plain_list.append(dicts['text'])
            if dicts['type'] == 'At':
                at_list.append(dicts['target'])
        if len(plain_list) > 0:
            returning['plain'] = plain_list
        if len(at_list) > 0:
            returning['at'] = at_list
        return returning
