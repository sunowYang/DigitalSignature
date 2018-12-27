#! coding=utf8

"""
    Start file for program
"""

import os
import sys
from bin import Run
from bin import log

# ********************************Get executing path******************************
if getattr(sys, 'frozen', False):
    BASE_PATH = os.path.dirname(sys.executable)
else:
    BASE_PATH = os.path.dirname(__file__)
# ********************************************************************************


LOG = log.MyLog(BASE_PATH, 'log.log')    # 创建日志对象
CONFIG_PATH = os.path.join(BASE_PATH, 'config', 'config.ini')

if __name__ == '__main__':
    # try:
        Run.run(LOG, CONFIG_PATH)
    # except Exception as e:
    #     LOG.logger.error(e)
    #     LOG.logger.info('========================END============================')
