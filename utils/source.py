import json
import os
import threading

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

    def gen_session(self):
        """
        Generate & verify a Mirai Session
        return format:
        {
        'sessionKey': 'ExampleString',
        'qq': 1234567890
        }
        """

        reply = requests.post(self.httpip + '//auth', data=json.dumps({"authKey": self.config_dict['authKey']}))
        reply_dict = json.loads(bytes.decode(reply.content))
        session = {"sessionKey": reply_dict['session'], "qq": self.config_dict['qq']}
        requests.post(self.httpip + '//verify', data=json.dumps(session))
        return session  # return session and qq in dict form

    async def websockets_receive(self, session: dict):
        uri = self.websockets_ip + '/all?sessionKey=' + session['sessionKey']
        with websockets.connect(uri) as current_ws_conn:
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
            reply_dict = json.loads(bytes.decode(reply.content))
            msg_id = reply_dict['messageId']
        finally:
            return msg_id


class MessageParser:
    def command_parse(self, content: dict):  # TODO: Implement stop all process
        if content['args'][0] == 'stop':
            raise NotImplementedError()
        return

    def console_input(self, using: bool):
        while using:
            text = input()
            command_tuple = text.split()
            content_dict = {
                'sender': 'console',
                'content': text,
                'args': command_tuple
            }
            self.command_parse(content_dict)
        return


def start_thread(func: callable, args: tuple, name=None):
    thread = threading.Thread(target=func, args=args, name=name)
    thread.setDaemon(True)
    thread.start()
    return thread
