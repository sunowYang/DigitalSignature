#! coding=utf8

"""
    The main progress of program:
        1.Get config data
        2.Download and uncompress the packages
        3.Get information of all files
            1.Get digital signature of file
            2.Get version info of file
        4.Write results to excel
"""

import os
import time
from download import Download
from getfileinfo import FileOperation
from excel import WriteExcel
from PyQt5.QtCore import pyqtSignal, QObject

EXCEL_VOL_TITLES = ['FileName', 'Issued to', 'Expires', 'Count', 'Result']
EXCEL_COMPARE_TITLES = ['FileName', 'Issued to', 'Issued-new', 'Expires', 'Expires-new', 'Count', 'Count-new', 'Result']


class Run(QObject):
    progress_signal = pyqtSignal(int, str)

    def __init__(self, base_path, parent=None):
        super(Run, self).__init__(parent)
        self.base_path = base_path
        self.target_path = os.path.join(base_path, 'download')
        self.data = {}
        self.excel_titles = []
        self.result_path = ''
        self.filter = []

    def get_file_digital_info(self, package_path, file_path):
        file_digital_file = {}
        file_operation = FileOperation()
        signature_info = file_operation.get_digital_signature_info(file_path)
        # 给excel列赋初值
        for title in self.excel_titles:
            file_digital_file[title] = ''
        if 'FileName' in self.excel_titles:
            file_digital_file['FileName'] = file_path[len(package_path) + 1:]
        if 'Count' in self.excel_titles:
            file_digital_file['Count'] = str(len(signature_info))

        # 从数字签名信息中获取相应信息，多个签名就叠加
        for _info in signature_info:
            if 'Issued to' in self.excel_titles:
                file_digital_file['Issued to'] += _info['Issued to'] + '\n'
            if 'Expires' in self.excel_titles:
                file_digital_file['Expires'] += _info['Expires'] + '\n'
            if 'hash_method' in self.excel_titles:
                file_digital_file['hash_method'] += _info['hash_method'] + '\n'
            if 'Issued by' in self.excel_titles:
                file_digital_file['Issued by'] += _info['Issued by'] + '\n'
            if 'SHA1 hash:' in self.excel_titles:
                file_digital_file['SHA1 hash:'] += _info['SHA1 hash:'] + '\n'

        return file_digital_file

    def start(self, data):
        try:
            self.data = data
            # 初始化参数
            compared, self.filter, self.excel_titles, self.result_path = self.init_data()
            # 下载和解压
            uncompress_path = self.download()
            excel = WriteExcel(self.result_path)
            # 获取文件签名并写入结果文件
            if compared:
                self.compare(uncompress_path, excel)
            else:
                self.not_compare(uncompress_path, excel)
            self.progress_signal.emit(100, '任务完成')
        except Exception as e:
            self.progress_signal.emit(100, e.message)

    def compare(self, uncompress_path, excel):
        self.progress_signal.emit(50, '开始对比两个版本的文件签名信息')
        source_files = self.get_files(uncompress_path[0])
        compare_files = self.get_files(uncompress_path[1])
        row = 1
        for _file in compare_files:
            info = {}
            compare_file_path = os.path.join(uncompress_path[1], _file)
            compare_file_info = self.get_file_digital_info(uncompress_path[1], compare_file_path)
            info['FileName'] = _file
            info['Issued-new'] = compare_file_info['Issued to']
            info['Expires-new'] = compare_file_info['Expires']
            info['Count-new'] = compare_file_info['Count']
            # 判断老版本中是否存在该文件，存在就获取签名并对比
            if _file in source_files:
                source_file_path = os.path.join(uncompress_path[0], _file)
                source_file_info = self.get_file_digital_info(uncompress_path[0], source_file_path)
                info['Issued to'] = source_file_info['Issued to']
                info['Expires'] = source_file_info['Expires']
                info['Count'] = source_file_info['Count']
                # 判断两个版本中的签名信息是否相等
                if source_file_info['Issued to'] == compare_file_info['Issued to'] and \
                        source_file_info['Expires'] == compare_file_info['Expires']:
                    result = 'success'
                elif source_file_info['Issued to'] == compare_file_info['Issued to'] and \
                        source_file_info['Expires'] != compare_file_info['Expires']:
                    result = 'time different'
                elif source_file_info['Issued to'] != compare_file_info['Issued to'] and \
                        source_file_info['Expires'] == compare_file_info['Expires']:
                    result = 'signature different'
                else:
                    result = 'all different'
                # 删除已对比的文件
                source_files.remove(_file)
                compare_files.remove(_file)
            else:
                result = 'new file'
            info['Result'] = result
            self.write_result(excel, row, info)
            row += 1
        # 判断source_files中是否还有未对比的文件
        if len(source_files) != 0:
            info = {}
            for _file in source_files:
                info['FileName'] = _file
                source_file_path = os.path.join(uncompress_path[0], _file)
                source_file_info = self.get_file_digital_info(uncompress_path[0], source_file_path)
                info['Issued to'] = source_file_info['Issued to']
                info['Expires'] = source_file_info['Expires']
                info['Count'] = source_file_info['Count']
                info['Result'] = 'no file'
                self.write_result(excel, row, info)
                row += 1

    def not_compare(self, uncompress_path, excel):
        row = 1
        for root, dirs, files in os.walk(uncompress_path):
            for _file in files:
                if self.file_filter(_file):
                    file_info = self.get_file_digital_info(uncompress_path, os.path.join(root, _file))
                    self.write_result(excel, row, file_info)
                    row += 1

    def file_filter(self, _file):
        """
            判断文件是否符合筛选要求，符合就返回True
        """
        if self.filter is None:
            return _file
        for __filter in self.filter:
            if __filter.startswith('*.') and _file.endswith(__filter[1:]):
                return True
            elif __filter in _file:
                return True

    def get_files(self, path):
        """
            获取文件夹下所有符合筛选的文件,并且返回文件的相对路径(方便后续对比)
        """
        _files = []
        for root, dirs, files in os.walk(path):
            for _file in files:
                if self.file_filter(_file):
                    _files.append(os.path.join(root, _file)[len(path) + 1:])
        return _files

    def init_data(self):
        """
            解析界面传来的参数， 主要是判断对比和筛选参数，还有获取Excel title
        @return: bool:compared list:filter
        """
        if 'compare' in self.data.keys():
            compared = True
        else:
            compared = False
        if 'filter' in self.data.keys():
            _filter = [self.data['filter']] if ',' not in self.data['filter'] else self.data['filter'].split(',')
        else:
            _filter = False
        # 获取Excel表头
        if compared:
            excel_titles = EXCEL_COMPARE_TITLES
        else:
            excel_titles = EXCEL_VOL_TITLES
        # 获取结果文件位置
        result_path = os.path.join(self.base_path, 'result')
        if not os.path.exists(result_path):
            os.mkdir(result_path)
        result_name = 'result_' + time.strftime('%Y%m%d_%H%M%S', time.localtime()) + '.xls'
        return compared, _filter, excel_titles, os.path.join(result_path, result_name)

    def download(self):
        """
            下载和解压安装包
        @return:
        """
        self.progress_signal.emit(5, '开始下载安装包')
        download = Download()
        source_path = self.data['source']
        target_path = download.download_file(source_path, self.target_path)
        self.progress_signal.emit(10, '下载完成，开始解压安装包')
        tool_path = os.path.join(self.base_path, 'tools', 'innounp.exe')
        download.uncompress(target_path, target_path[:-4], tool_path)
        download.download_file(target_path, target_path[:-4])
        if 'compare' in self.data.keys():
            # 下载要对比的安装包
            self.progress_signal.emit(20, '解压完成，开始下载要对比的安装包')
            compare_source_path = self.data['compare_source']
            compare_target_path = download.download_file(compare_source_path, self.target_path)
            self.progress_signal.emit(25, '下载完成，开始解压要对比的安装包')
            download.uncompress(compare_target_path, compare_target_path[:-4], tool_path)
            download.download_file(compare_target_path, compare_target_path[:-4])
            self.progress_signal.emit(40, '解压完成')
            return [target_path[:-4], compare_target_path[:-4]]
        else:
            return target_path[:-4]

    def write_result(self, excel, row, info):
        if row == 1:
            excel.create_new('Sheet1', self.excel_titles)
        print row
        print info
        excel.write_row_by_title(row, strings=info)  # 需修改


if __name__ == '__main__':
    excel = WriteExcel(r'C:\Users\Administrator\Desktop\TB_SCRIPT\DigitalSignature\result\abc.xls')
    titles = ['a', 'b', 'c']
    excel.create_new('Sheet1', 'a', 'v', 'vc')
