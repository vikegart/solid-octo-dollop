import logging

from controller import Controller

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    Controller.run(host='0.0.0.0', port=8081)
