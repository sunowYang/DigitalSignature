#! coding=utf8

import os
import win32api


class FileOperation:
    def __init__(self, file_path):
        if not os.path.exists(file_path):
            raise IOError('No found file:%s' % file_path)
        self.file_path = file_path
        self.contribution_info = {}

    def get_file_info(self, contribution_list):
        if not isinstance(contribution_list, list):
            raise ValueError('"get_file_info" function need a list, not %s' % type(contribution_list))
        try:
            lang, code_page = win32api.GetFileVersionInfo(self.file_path, '\\VarFileInfo\\Translation')[0]
            for contribution_name in contribution_list:
                str_info_path = u'\\StringFileInfo\\%04X%04X\\%s' % (lang, code_page, contribution_name)
                # print str_info
                self.contribution_info[contribution_name] = win32api.GetFileVersionInfo(self.file_path, str_info_path)
        except:
            pass
        return self.contribution_info

    def get_digital_signature_info(self, tool_path, contribution_list):
        if not isinstance(contribution_list, list):
            raise ValueError('"get_digital_signature_info" function need a list, not %s' % type(contribution_list))
        cmd_command = r'""%s" verify /v "%s"' % (tool_path, self.file_path)
        command_result = os.popen(cmd_command)
        for message in command_result.read().split('\n'):
            for contribution in contribution_list:
                if contribution in message:
                    if contribution == 'Expires':
                        self.contribution_info[contribution] = message.split(contribution+':')[1].strip()
                    else:
                        self.contribution_info[contribution] = message.split(':')[1].strip()
