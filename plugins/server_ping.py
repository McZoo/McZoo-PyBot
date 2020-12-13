import json
import socket
import struct

import utils

REGISTRY_NAME = 'server_ping'
VERSION_TUPLE = (0, 0, 1)
VERSION_STR = '0.0.1'


class StatusPing:
    """
    Get the ping status for the Minecraft server
    """

    def __init__(self, host='localhost', port=25565, timeout=5):
        """ Init the hostname and the port """
        self._host = host
        self._port = port
        self._timeout = timeout

    @staticmethod
    def _unpack_var_int(sock):
        """ Unpack the var int """
        data = 0
        for i in range(5):
            ordinal = sock.recv(1)

            if len(ordinal) == 0:
                break

            byte = ord(ordinal)
            data |= (byte & 0x7F) << 7 * i

            if not byte & 0x80:
                break

        return data

    @staticmethod
    def _pack_var_int(data):
        """ Pack the var int """
        ordinal = b''

        while True:
            byte = data & 0x7F
            data >>= 7
            ordinal += struct.pack('B', byte | (0x80 if data > 0 else 0))

            if data == 0:
                break

        return ordinal

    def _pack_data(self, data):
        """ Page the data """
        if type(data) is str:
            data = data.encode('utf8')
            return self._pack_var_int(len(data)) + data
        elif type(data) is int:
            return struct.pack('H', data)
        elif type(data) is float:
            return struct.pack('Q', int(data))
        else:
            return data

    def _send_data(self, connection, *args):
        """ Send the data on the connection """
        data = b''

        for arg in args:
            data += self._pack_data(arg)

        connection.send(self._pack_var_int(len(data)) + data)

    def _read_fully(self, connection, extra_var_int=False):
        """ Read the connection and return the bytes """
        packet_length = self._unpack_var_int(connection)
        packet_id = self._unpack_var_int(connection)
        byte = b''

        if extra_var_int:
            # Packet contained netty header offset for this
            if packet_id > packet_length:
                self._unpack_var_int(connection)

            extra_length = self._unpack_var_int(connection)

            while len(byte) < extra_length:
                byte += connection.recv(extra_length)

        else:
            byte = connection.recv(packet_length)

        return byte

    def get_status(self):
        """ Get the status response """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
            connection.settimeout(self._timeout)
            connection.connect((self._host, self._port))

            # Send handshake + status request
            self._send_data(connection, b'\x00\x00', self._host, self._port, b'\x01')
            self._send_data(connection, b'\x00')

            # Read response, offset for string length
            data = self._read_fully(connection, extra_var_int=True)

        # Load json and return
        response = json.loads(data.decode('utf8'))
        return response

    def get_stat_until_complete(self, logger: utils.Logger):
        res = None
        while res is None:
            try:
                res = self.get_status()
            except Exception as e:
                logger.stacktrace(e, 'fake')
        return res


def websockets_parser(parsed_msg: dict, logger: utils.Logger, session: utils.Session, cfg: utils.Config):
    if logger:
        pass
    if parsed_msg.get('plain') is not None:
        i = ''
        for u in parsed_msg['plain']:
            i += u
        args = str.split(i, ' ')
        for u in args:
            u.replace('\n', '')
        if args[0] == '!!server_ping':
            if len(args) >= 2:
                if len(args) == 3:
                    status = StatusPing(args[1], int(args[2]))
                else:
                    status = StatusPing(args[1])
                try:
                    res = status.get_stat_until_complete(logger)
                    server_version: str = str.replace(res['version']['name'], 'Requires ', '')
                    player: list = [res['players']['online'], res['players']['max']]
                    desc: list[str] = str.split(res['description'], '\n')
                    for v in desc:
                        v.strip(' ')
                    icon_str = res['favicon']
                    reply_list = [
                        {
                            "type": "Image",
                            "url": icon_str
                        },
                        {
                            "type": "Plain",
                            "text": '{0}\r\n'.format(args[1])
                        },
                        {
                            "type": "Plain",
                            "text": '服务器版本：{0}\r\n'.format(server_version)
                        },
                        {
                            "type": "Plain",
                            "text": '玩家数：{0}/{1}\r\n'.format(player[0], player[1])
                        }
                    ]
                    for v in desc:
                        reply_list.append({
                            "type": "Plain",
                            "text": '{0}\r\n'.format(v)
                        })
                except Exception as e:
                    logger.stacktrace(e, 'error')
                    reply_list = [
                        {
                            "type": "Plain",
                            "text": '参数错误\r\n'
                        }
                    ]
            else:
                reply_list = [
                    {
                        "type": "Plain",
                        "text": '参数错误\r\n'
                    }
                ]
            utils.send_list(cfg, session.session_dict, parsed_msg['group_id'], reply_list, 'group')
