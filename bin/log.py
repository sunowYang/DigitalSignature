#! coding=utf8

import os
import logging


class MyLog:
    def __init__(self, log_path, log_name, name='YGX'):
        self.name = name
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        self.log_dir = os.path.join(log_path, log_name)
        if not os.path.exists(self.log_dir):
            open(self.log_dir, 'w').close()
        # create logger
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
        # create handler for output to log and console
        output_log = logging.FileHandler(self.log_dir)
        console_log = logging.StreamHandler()

        # set log lowest output
        output_log.setLevel(logging.DEBUG)
        console_log.setLevel(logging.DEBUG)

        # set log formatter
        output_log.setFormatter(self.formatter)
        console_log.setFormatter(self.formatter)
        # add handler to log
        self.logger.addHandler(output_log)
        self.logger.addHandler(console_log)

