import os
import sys
import time

sys.path.append('.')
if __name__ == '__main__':
    if os.path.exists('./stop.lck'):
        os.remove('./stop.lck')
    while True:
        input_str = input()
        if input_str == 'stop':
            stop_file_path = os.path.abspath('./stop.lck')
            open(stop_file_path, 'w')
            time.sleep(0.5)
            os.remove(stop_file_path)
            sys.exit()
        else:
            try:
                eval(input_str)
            except Exception as e:
                print(e)
