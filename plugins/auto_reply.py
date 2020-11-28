import utils


def websockets_parser(parsed_msg: dict, logger: utils.Logger, session: utils.Session, cfg: utils.Config):
    if parsed_msg.get('at') is not None:
        for i in parsed_msg['at']:
            if i == session.qq:
                logger.log('info', 'Start response!')
                reply_list = [
                    {
                        "type": "At",
                        "target": parsed_msg['sender_id'],
                    }, {
                        "type": "Plain",
                        "text": "w?"}
                ]
                utils.send_list(cfg, session.session_dict, parsed_msg['sender_id'], reply_list, 'group')
# TODO
