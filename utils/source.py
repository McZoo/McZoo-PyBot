import importlib
import json
import multiprocessing
import os
import sys

import requests
import ruamel.yaml as yaml
import websockets


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

    class Session:
        def __init__(self, mirai_inst):
            """
            Automatically generates session
            """
            self.session_dict = self.gen()
            self.session_key = self.session_dict['session']
            self.qq = self.session_dict['qq']
            self.mirai_inst = mirai_inst

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

    async def websockets_receive(self, session: dict):
        url = self.websockets_ip + '/all?sessionKey=' + session['sessionKey']
        with websockets.connect(url) as current_ws_conn:
            message_dict = json.loads(await current_ws_conn.recv())
        return message_dict

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
            extra_uri = '/sendFriendMessage'
        else:
            extra_uri = '/sendGroupMessage'
        uri = self.httpip + extra_uri
        send_data = json.dumps(message_dict)
        reply = requests.post(uri, send_data)
        msg_id = -1
        try:
            reply_dict = json.loads(reply.text)
            msg_id = reply_dict['messageId']
        finally:
            return msg_id


class MessageParser:
    def __init__(self, mirai_inst, process_inst):
        self.mirai_inst = mirai_inst
        self.process_inst = process_inst

    def command_parse(self, content: dict):  # TODO: Implement stop all process
        if content['args'][0] == 'stop':
            sys.exit()
        try:
            Process.proc_call(self.process_inst, content['args'][0], content['args'][1], content['args'][2:])
        except NotImplementedError():
            print("Not Implemented\n")
        return

    def console_input(self, using: bool):
        while using:
            text = input()
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
        self.pool = multiprocessing.Pool()

    def proc_call(self, mod: str, func: str, args: list):
        """
        Call a function
        :param mod:
        :param func:
        :param args:
        :return:
        """
        module = importlib.import_module(mod)
        caller = getattr(module, func)
        self.pool.apply_async(caller, args)
        return

    def shut(self):
        """
        Closes the pool
        """
        self.pool.close()
