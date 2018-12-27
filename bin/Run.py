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
from Config import ConfigRead
from DownLoadAndUncompress import Download
from getfileinfo import FileOperation
from WriteResult import WriteResult, ReadExcel

EXCEL_VOL_TITLES = ['FileName', 'Issued to', 'Expires', 'Count', 'Result']


def get_files(path):
    _files = []  # 返回值，该目录下所有文件路径
    if not os.path.exists(path) or os.path.isfile(path):
        raise IOError('No found path:%s' % path)
    for root, dirs, files in os.walk(path):
        for _file in files:
            # 循环找exe、dll、sys文件的签名信息，每个文件写一次excel
            if _file.endswith('exe') or _file.endswith('dll') or _file.endswith('sys'):
                _files.append(os.path.join(root, _file))
    return _files


class Run:
    def __init__(self, log, config_path):
        self.log = log
        self.config_path = config_path

        self.data = ConfigRead(self.log, self.config_path).read()  # 解析配置文件
        self.uncompressed_paths = Download(self.log, self.data).download()  # 下载并解压安装包
        self.excel_vol_titles = self.get_excel_titles()  # excel表头，获取的数据类型

        self.package_names = self.data['versions'].split(',') if ',' in self.data['versions'] else [
            self.data['versions']]

    def get_excel_titles(self):
        """
        直接传所有数据是想把数据处理部分放在各个函数里面，减少主函数代码，增加易读性
        如果config.ini没有参数 excel_titles或值为“0”，那么就使用默认值
        :return: 返回excel表头
        """
        if 'excel_titles' in self.data.keys():
            if ',' in self.data['excel_titles']:
                excel_titles = self.data['excel_titles'].split(',')
            elif self.data['excel_titles'] == '0':
                excel_titles = EXCEL_VOL_TITLES
            else:
                excel_titles = [self.data['excel_titles']]
        else:
            excel_titles = EXCEL_VOL_TITLES
        return excel_titles

    def get_file_digital_info(self, package_path, file_path):
        file_digital_file = {}
        file_operation = FileOperation()
        signature_info = file_operation.get_digital_signature_info(file_path)
        # 给excel列赋初值
        for title in self.excel_vol_titles:
            file_digital_file[title] = ''
        if 'FileName' in self.excel_vol_titles:
            file_digital_file['FileName'] = file_path[len(package_path):]  # 这里只截取后面部分路径，因为版本号会变化
        if 'Count' in self.excel_vol_titles:
            file_digital_file['Count'] = str(len(signature_info))

        # 从数字签名信息中获取相应信息，多个签名就叠加
        for _info in signature_info:
            if 'Issued to' in self.excel_vol_titles:
                file_digital_file['Issued to'] += _info['Issued to'] + '\n'
            if 'Expires' in self.excel_vol_titles:
                file_digital_file['Expires'] += _info['Expires'] + '\n'
            if 'hash_method' in self.excel_vol_titles:
                file_digital_file['hash_method'] += _info['hash_method'] + '\n'
            if 'Issued by' in self.excel_vol_titles:
                file_digital_file['Issued by'] += _info['Issued by'] + '\n'
            if 'SHA1 hash:' in self.excel_vol_titles:
                file_digital_file['SHA1 hash:'] += _info['SHA1 hash:'] + '\n'

        return file_digital_file


def run(log, config_path):
    _run = Run(log, config_path)
    if len(_run.uncompressed_paths) == 0:
        return
    # 1、遍历每个版本
    for package_path in _run.uncompressed_paths:
        log.logger.info('Start to get package info:%s' % package_path)
        for _package_name in _run.package_names:  # 获取当前安装包简称,生成结果文件使用
            if package_path.endswith(_package_name[:-4]):
                package_name = _package_name
                break
        else:
            raise IOError('No found version uncompressed path:%s' % package_path)
        # 2、判断该版本的基带excel是否存在，不存在就生成基带版本，存在就对比签名是否一致
        base_excel_path = os.path.join(config_path[:-18], 'config')  # 对比excel路径
        base_excel_name = package_name[:-4] + '.xls'  # 对比excel名称
        # 3.1 生成版本的基带excel
        if not os.path.exists(os.path.join(base_excel_path, base_excel_name)):
            row = 1  # 写入excel起始行
            for _file in get_files(package_path):
                file_info = _run.get_file_digital_info(package_path, _file)  # 文件的签名信息
                result = WriteResult(base_excel_path, base_excel_name)
                result.write_excel(_run.excel_vol_titles, row, file_info)
                row += 1
        # 3.2 对比基带版本
        else:
            row = 1
            result_path = os.path.join(config_path[:-18], 'result')
            result_name = package_name[:-4] + '_result_' + time.strftime('%Y%m%d_%H%M%S', time.localtime()) + '.xls'

            for _file in get_files(package_path):
                now_file_info = _run.get_file_digital_info(package_path, _file)  # 新文件的签名信息
                excel_file_info = {}                                             # 旧文件的签名信息

                read_excel = ReadExcel(os.path.join(base_excel_path, base_excel_name))
                excel_file_name_list = read_excel.read_col(0)
                # 判断基带excel是否记录该文件的签名
                if _file[len(package_path):] in excel_file_name_list:
                    file_index = excel_file_name_list.index(_file[len(package_path):])
                    excel_file_info['Issued to'] = read_excel.read(file_index, 1)
                    excel_file_info['Expires'] = read_excel.read(file_index, 2)
                    # Issued to和Expires相等就认为签名正确
                    if now_file_info['Issued to'].strip() == excel_file_info['Issued to'] and \
                            now_file_info['Expires'].strip() == excel_file_info['Expires']:
                        compare_result = 'success'
                    elif now_file_info['Issued to'].strip() == excel_file_info['Issued to'] and \
                            now_file_info['Expires'].strip() != excel_file_info['Expires']:
                        compare_result = 'time failed'
                    elif now_file_info['Issued to'].strip() != excel_file_info['Issued to'] and \
                            now_file_info['Expires'].strip() == excel_file_info['Expires']:
                        compare_result = 'name failed'
                    else:
                        compare_result = 'failed'
                else:
                    compare_result = 'no file'
                now_file_info['Result'] = compare_result
                # 写入excel
                result = WriteResult(result_path, result_name)
                result.write_excel(_run.excel_vol_titles, row, now_file_info)
                row += 1
