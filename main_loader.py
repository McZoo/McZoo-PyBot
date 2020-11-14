import os
from utils import source
import multiprocessing
if __name__ == '__main__':
    yaml_path: str = os.path.join(os.getcwd(), 'config.yml')
    mirai = source.Mirai(yaml_path)
    proc = source.Process()
    session = mirai.Session(mirai)
    ws = mirai.Websockets(mirai, session)
    msg_parser = source.MessageParser(mirai, proc, session)
    msg_parser_p = multiprocessing.Process(target=msg_parser.console_input, args=(True,), daemon=True)
    msg_cycle_p = multiprocessing.Process(target=ws.get_msg_cycle, args=(True,))
    msg_cycle_p.start()
    msg_parser_p.start()
    msg_parser_p.join()
