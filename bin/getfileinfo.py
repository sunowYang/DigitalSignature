#! coding=utf8

import os
import sys
import win32api

# ********************************Get executing path******************************
if getattr(sys, 'frozen', False):
    BASE_PATH = os.path.dirname(sys.executable)
else:
    BASE_PATH = os.path.dirname(__file__)
# ********************************************************************************


class FileOperation:
    def __init__(self):

        self.tool_path = os.path.join(BASE_PATH[:-3], 'tools', 'signtool.exe')
        self.info = {}

    def get_file_info(self, file_path, contribution_list):
        if not isinstance(contribution_list, list):
            raise ValueError('"get_file_info" function need a list, not %s' % type(contribution_list))
        try:
            lang, code_page = win32api.GetFileVersionInfo(file_path, '\\VarFileInfo\\Translation')[0]
            for contribution_name in contribution_list:
                str_info_path = u'\\StringFileInfo\\%04X%04X\\%s' % (lang, code_page, contribution_name)
                if contribution_name == 'signature':
                    self.get_digital_signature_info(file_path)
                else:
                    self.info[contribution_name] = win32api.GetFileVersionInfo(file_path, str_info_path)
        except:
            pass
        return self.info

    def get_digital_signature_info(self, file_path):
        # 判断文件是否存在
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            raise IOError('No found file:%s' % file_path)
        cmd_command = r'""%s" verify /all /v "%s"' % (self.tool_path, file_path)
        command_result = os.popen(cmd_command)
        # 读取打印信息，并分析结果
        signature_list = []
        signature_info = {}
        for msg in command_result.read().split('\n'):
            if 'Signature Index' in msg:
                # 判断签名序号，如果不是第一个签名，就将上一个签名信息加入list
                if msg.split(' ')[2] != '0':
                    signature_list.append(signature_info)
                    signature_info = {}
                signature_info['signature_index'] = msg.split(' ')[2]
            elif 'Hash of file' in msg:
                signature_info['hash_method'] = msg.split(' ')[3][1:-2]
            elif 'Issued to' in msg:
                signature_info['Issued to'] = msg.split(': ')[1]
            elif 'Issued by' in msg:
                signature_info['Issued by'] = msg.split(': ')[1]
            elif 'Expires' in msg:
                signature_info['Expires'] = msg.split(':   ')[1]
            elif 'SHA1 hash:' in msg:
                signature_info['SHA1 hash'] = msg.split(': ')[1]
        # 加入最后一个签名信息
        if len(signature_info) != 0:
            signature_list.append(signature_info)
        self.info['signature'] = signature_list
        return signature_list


if __name__ == '__main__':
    file_path1 = r'C:\Program Files (x86)\EaseUS\Todo Backup\bin\loader.exe'
    contr_list = ['sha256', 'Issued to', 'Issued by', 'Expires', 'SHA1 hash']
    file_info = FileOperation()
    print file_info.get_digital_signature_info(file_path1)
