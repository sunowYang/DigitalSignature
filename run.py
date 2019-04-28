#! coding=utf8

"""
    Start file for program
"""

import os
import sys
from bin import log
from bin.ui import run

# ********************************Get executing path******************************
if getattr(sys, 'frozen', False):
    BASE_PATH = os.path.dirname(sys.executable)
else:
    BASE_PATH = os.path.dirname(__file__)
# ********************************************************************************


LOG = log.MyLog(BASE_PATH, 'log.log')

if __name__ == '__main__':
    try:
        run(LOG, BASE_PATH)
    except Exception as e:
        LOG.logger.error(e)
    finally:
        LOG.logger.info('========================END============================')
