import os

import utils
import multiprocessing
if __name__ == '__main__':
    yaml_path: str = os.path.join(os.getcwd(), 'config.yml')
    mirai = utils.Mirai(yaml_path)
    proc = utils.Process()
    session = mirai.Session(mirai)
    ws = mirai.Websockets(mirai, session)
    msg_parser = utils.MessageParser(mirai, proc, session)
    msg_parser_p = multiprocessing.Process(target=msg_parser.console_input, args=(True,), daemon=True)
    msg_cycle_p = multiprocessing.Process(target=ws.get_msg_cycle, args=(True,))
    msg_cycle_p.start()
    msg_parser_p.start()
    msg_parser_p.join()
