import sys

if __name__ == '__main__':
    while True:
        input_str = input()
        if input_str == 'stop':
            fs = open('./stop.lck', 'w')
            fs.close()
            sys.exit()
