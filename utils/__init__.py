import importlib
import json
import multiprocessing
import os
import sys

import requests
import websockets
from ruamel import yaml as yaml


class Mirai:
    """
    A class for Mirai Post & Receive
    """

    def __init__(self, configs_path: str):
        """
        Automatically load yaml config
        """

        yaml_fs = open(os.path.abspath(configs_path), "r")
        self.config_dict = yaml.load(yaml_fs, Loader=yaml.Loader)
        self.httpip = self.config_dict['HttpIP']
        self.websockets_ip = self.config_dict['Websockets_IP']
        yaml_fs.close()

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
                print(cur_msg)

    class Session:
        def __init__(self, mirai_inst):
            """
            Automatically generates session
            """
            self.mirai_inst = mirai_inst
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

            reply = requests.post(self.mirai_inst.httpip + '/auth',
                                  data=json.dumps({"authKey": self.mirai_inst.config_dict['authKey']}))
            reply_dict = json.loads(reply.text)
            session = {"sessionKey": reply_dict['session'], "qq": self.mirai_inst.config_dict['qq']}
            requests.post(self.mirai_inst.httpip + '/verify', data=json.dumps(session))
            return session  # return session and qq in dict form

        def release(self):
            """
                    release a Mirai Session
                    :return: nothing
                    """
            requests.post(self.mirai_inst.httpip + '/release', data=json.dumps(self.session_dict))

    def send_text(self, session: dict, target: int, text: str, target_type: str = 'group'):
        """
        Send a plain text message to a friend/group
        returns message id if success , else -1
        :param session: dict from Mirai.gen_session()
        :param target: int
        :param text: string
        :param target_type: 'friend' or 'group'
        :return:
        """
        message_dict = {
            'sessionKey': session['session'],
            'target': target,
            'messageChain': [
                {
                    'type': 'Plain',
                    'text': text
                }
            ]
        }
        if target_type == 'friend':
            extra_url = '/sendFriendMessage'
        else:
            extra_url = '/sendGroupMessage'
        uri = self.httpip + extra_url
        send_data = json.dumps(message_dict)
        reply = requests.post(uri, send_data)
        msg_id = -1
        try:
            reply_dict = json.loads(reply.text)
            msg_id = reply_dict['messageId']
        finally:
            return msg_id


class MessageParser:
    def __init__(self, mirai_inst, process_inst, session_inst):
        self.mirai_inst = mirai_inst
        self.process_inst = process_inst
        self.session_inst = session_inst

    def command_parse(self, content: dict):  # TODO: Implement stop all process
        if content['sender'] == 'console':
            if content['args'][0] == 'stop':
                sys.exit()
            try:
                Process.proc_call(self.process_inst, content['args'][0], content['args'][1:])
            except NotImplementedError():
                print("Not Implemented\n")
            return

    def console_input(self, using: bool):
        while using:
            text = input('>')
            command_list: list = text.split()
            content_dict = {
                'sender': 'console',
                'content': text,
                'args': command_list
            }
            self.command_parse(content_dict)
        return


class Process:
    def __init__(self):
        self.counter: int = 0

    def proc_call(self, mod_func: str, args: list):
        """
        Call a function using nod_func and args
        :param mod_func:
        :param args:
        :return:
        """
        self.counter += 1
        usage_list = mod_func.split('.')
        if len(usage_list) > 2:
            mod_path = '.'.join(usage_list[0:-2])
        else:
            if len(usage_list) == 2:
                mod_path = usage_list[0]
            else:
                mod_path = 'builtins'
        func = usage_list[-1]
        handler = None
        try:
            module = importlib.import_module(mod_path)
            caller = getattr(module, func)
            handler = multiprocessing.Process(target=caller, args=tuple(args), daemon=True)
        except NotImplementedError:
            raise
        finally:
            return handler
