#! coding=utf8

from ConfigParser import ConfigParser
import os


class Config:
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
        self.config = ConfigParser()

    def read(self):
        dic = {}
        self.log.logger.info('Read config.ini')
        if not os.path.exists(self.config_path):
            raise IOError('No found config file')

        self.config.read(self.config_path)
        # Get all sections and keys
        for section in self.config.sections():
            for key in self.config.options(section):
                dic[key] = self.config.get(section, key)
        return dic

    def write(self, data):
        open(self.config_path, 'w').close()
        self.config.read(self.config_path)
        self.config.add_section('signature')
        for key, value in data.items():
            if isinstance(value, list) and len(value) > 1:
                value = ','.join(iter(value))
            self.config.set('signature', key, value)
        self.config.write(open(self.config_path, 'w'))


if __name__ == '__main__':
    config = Config('log', r'd:\1.ini')
    config.write({'a': '123', 'b': '321'})

