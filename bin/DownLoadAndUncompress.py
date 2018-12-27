#! coding=utf8


import os
import sys
import urllib
from shutil import copy
from log import MyLog

reload(sys)
sys.setdefaultencoding('utf8')


class Download:
    def __init__(self, log, data):
        self.log = log
        if not isinstance(data, dict):
            raise ValueError('Download:data is not a dict')
        if 'versions' not in data.keys() or data['versions'] is None:
            raise ValueError('Download:data not has key of versions or the value is None')
        if 'downloadpath' not in data.keys() or data['downloadpath'] is None:
            raise ValueError('Download:data not has key of download_path or the value is None')
        if 'destinationpath' not in data.keys() or data['destinationpath'] is None:
            raise ValueError('Download:data not has key of destination_path or the value is None')
        if 'uncompresstoolpath' not in data.keys() or data['uncompresstoolpath'] is None:
            raise ValueError('Download:data not has key of UncompressToolPath or the value is None')
        self.versions = [data['versions']] if ',' not in data['versions'] else data['versions'].split(',')
        self.download_path = data['downloadpath'].decode('utf8')
        self.destination_path = data['destinationpath'].decode('utf8')
        self.uncompress_tool_path = data['uncompresstoolpath'].decode('utf8')
        if not os.path.exists(self.destination_path):
            os.makedirs(self.destination_path)
        self.version_path_list = []   # return a list of local file path

    def download(self):
        # if download from network,
        if self.download_path.startswith('http'):
            self.log.logger.info('Download file from network')
            # not complete
        else:
            self.log.logger.info('Download file from nas or other')
            try:
                self.copy_from_nas()
                # self.version_path_list.append(r'C:\setup\package\TodoBackup_12.0_Enterprise_Trial') # ���Դ���
            except Exception.message as e:
                self.log.logger.warn('Download failed:%s' % e)
                # raise IOError('Download failed:%s' % e)
        return self.version_path_list

    def copy_from_nas(self):
        # match the version of packages
        for version in self.versions:
            for item in os.listdir(self.download_path):
                version_path = os.path.join(self.download_path, item)
                if os.path.isfile(version_path) and version in item:
                    self.log.logger.info('Find file:%s' % version)
                    # copy version
                    self.log.logger.info('Start to copy file:%s' % version)
                    copy(version_path, self.destination_path)
                    self.log.logger.info('Copy file end')
                    # uncompress version
                    self.log.logger.info('Start to uncompress file')
                    self.version_path_list.append(
                            self.uncompress(os.path.join(self.destination_path, item)))
                    self.log.logger.info('Uncompress file end')
                    break
            else:
                self.log.logger.warn('Not find file:%s' % version)

    def uncompress(self, package_path):
        uncompress_path = package_path[:-4]
        tool_path = os.path.join(self.uncompress_tool_path, 'innounp.exe')
        # if package exist
        if not os.path.exists(package_path):
            raise IOError('No found package:%s' % package_path)
        # remove uncompressed dir if exists
        if os.path.exists(uncompress_path):
            if os.system('rd /S /Q "%s"' % uncompress_path) != 0:
                raise SyntaxError('Delete existing folder error:%s' % uncompress_path)
        # if has uncompress tool
        if not os.path.exists(tool_path):
            raise IOError('No found uncompress tool')
        uncompress_command = r'""%s" -q -x "%s" -d"%s"' % (tool_path, package_path, uncompress_path)
        if os.system(uncompress_command) != 0:
            raise SyntaxError('Execute uncompress command error')
        return uncompress_path

# if __name__ == '__main__':
#     from_path = r'\\192.168.1.110\��Ʒ����\��ʱ�汾\TB\11.0\2017-12-06_E'
#     to_path = r'c:\setup\package'
#     version = ['TodoBackup_11.0_Enterprise_Trial.exe']
#     LOG = MyLog(to_path, 'log.log')
#     download = Download(LOG, data)
#     print download.download()
