#! coding=utf8

from ConfigParser import ConfigParser
import os


class ConfigRead:
    """
        @requires:
                log-- an object for writing log
                config_path-- path of config file
        @return:
                a dictionary of data
        Read the config file and return
    """
    def __init__(self, log, config_path):
        self.config_path = config_path
        self.log = log

    def read(self):
        dic = {}
        self.log.logger.info('Read config.ini')
        if not os.path.exists(self.config_path):
            raise IOError('No found config file')

        config = ConfigParser()
        config.read(self.config_path)
        # Get all sections and keys
        for section in config.sections():
            for key in config.options(section):
                dic[key] = config.get(section, key)
        return dic

