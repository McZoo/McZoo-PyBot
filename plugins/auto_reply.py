import re
import time

import utils

REGISTRY_NAME = 'group_auto_reply'


def websockets_parser(parsed_msg: dict, logger: utils.Logger, session: utils.Session, cfg: utils.Config):
    if logger:
        pass
    if parsed_msg.get('at') is not None:
        for i in parsed_msg['at']:
            if i == session.qq:
                reply_list = [
                    {
                        "type": "At",
                        "target": parsed_msg['sender_id'],
                    }, {
                        "type": "Plain",
                        "text": "w?"}
                ]
                utils.send_list(cfg, session.session_dict, parsed_msg['group_id'], reply_list, 'group')
    if parsed_msg.get('plain') is not None:
        for i in parsed_msg['plain']:
            if re.search(r'ping', i) is not None:
                reply_list = [
                    {
                        "type": "At",
                        "target": parsed_msg['sender_id'],
                    }, {
                        "type": "Plain",
                        "text": "pong!"}
                ]
                utils.send_list(cfg, session.session_dict, parsed_msg['group_id'], reply_list, 'group')
            if re.search(r'怎么红名', i) is not None:
                reply_list = [
                    {
                        "type": "At",
                        "target": parsed_msg['sender_id'],
                    }, {
                        "type": "Plain",
                        "text": "玩家挖掘积分（TAB的数值）达到4000分自动红名"}
                ]
                utils.send_list(cfg, session.session_dict, parsed_msg['group_id'], reply_list, 'group')
            if re.search(r'怎么蓝名', i) is not None:
                reply_list = [
                    {
                        "type": "At",
                        "target": parsed_msg['sender_id'],
                    }, {
                        "type": "Plain",
                        "text": "红名后填写问卷：https://wj.qq.com/s2/6061246/4e09 并联系服主，若未通过客观+主观题测试，被已蓝名成员的印象推荐获得蓝名"}
                ]
                utils.send_list(cfg, session.session_dict, parsed_msg['group_id'], reply_list, 'group')
            if re.search(r'怎么金名', i) is not None:
                reply_list = [
                    {
                        "type": "At",
                        "target": parsed_msg['sender_id'],
                    }, {
                        "type": "Plain",
                        "text": "成年人赞助腐竹128"}
                ]
                utils.send_list(cfg, session.session_dict, parsed_msg['group_id'], reply_list, 'group')
            if re.search(r'怎么[\u4e00-\u9fa5]名', i) is not None:
                if (re.search(r'怎么金名', i) is None) and (re.search(r'怎么蓝名', i) is None) and (
                        re.search(r'怎么红名', i) is None):
                    reply_list = [
                        {
                            "type": "At",
                            "target": parsed_msg['sender_id'],
                        }, {
                            "type": "Plain",
                            "text": "你不会想知道的"}
                    ]
                    utils.send_list(cfg, session.session_dict, parsed_msg['group_id'], reply_list, 'group')
            if re.search(r'错别字', i) is not None:
                reply_list = [
                    {
                        "type": "Plain",
                        "text": "请大家领会精神"}
                ]
                utils.send_list(cfg, session.session_dict, parsed_msg['group_id'], reply_list, 'group')
            if re.search(r'(现在时间)|(北京时间)', i) is not None:
                reply_list = [
                    {
                        "type": "Plain",
                        "text": '现在是' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}
                ]
                utils.send_list(cfg, session.session_dict, parsed_msg['group_id'], reply_list, 'group')
            if re.search(r'!!help', i) is not None:
                reply_list = [
                    {
                        "type": "Plain",
                        "text": 'at我可得到 w?\r\n'},
                    {
                        "type": "Plain",
                        "text": '报时：北京时间 或 现在时间\r\n'
                    },
                    {
                        "type": "Plain",
                        "text": '其他自动回复可自行探索'
                    },

                ]
                utils.send_list(cfg, session.session_dict, parsed_msg['group_id'], reply_list, 'group')
# TODO
