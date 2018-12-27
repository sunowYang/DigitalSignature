#! coding=utf8

import os
import xlwt
import xlrd
from xlutils.copy import copy


class WriteResult:
    def __init__(self, result_path, result_name):
        if not os.path.exists(result_path):
            os.makedirs(result_path)
        self.result_path = os.path.join(result_path, result_name)
        self.result_name = result_name
        self.col_number = 0
        self.vol_number = 0


    @staticmethod
    def set_style(height, colour_index=4, bold=False, name='Times New Roman'):
        style = xlwt.XFStyle()
        font = xlwt.Font()
        font.name = name
        font.bold = bold
        font.colour_index = colour_index
        font.height = height
        style.font = font
        return style

    def write_excel(self, vol_titles, row, data):
        # 不存在就创建一个excel
        if not os.path.exists(self.result_path):
            workbook = xlwt.Workbook()
            sheet = workbook.add_sheet('sheet1', cell_overwrite_ok=True)
            for i in range(len(vol_titles)):
                sheet.write(0, i, vol_titles[i])
            workbook.save(self.result_path)
        # copy一个副本，方便追加写
        file_open = xlrd.open_workbook(self.result_path)
        file_copy = copy(file_open)
        # 写入值
        sheet1 = file_open.sheet_by_name('sheet1')
        for key in data.keys():
            vol = 0
            # 根据key找到对应列，然后写入值
            for i in range(len(data)):
                if sheet1.row_values(0)[i] == key:
                    vol = i
                    break
            file_copy.get_sheet(0).write(row, vol, data[key].strip())
        file_copy.get_sheet(0).col(0).width = 8000
        file_copy.get_sheet(0).col(1).width = 13000
        file_copy.get_sheet(0).col(2).width = 7000
        file_copy.save(self.result_path)

    def write_result(self, row, result):
        file_open = xlrd.open_workbook(self.result_path)
        file_copy = copy(file_open)
        # 写入值
        sheet1 = file_open.sheet_by_name('sheet1')
        # 根据key找到对应列，然后写入结果
        for i in range(sheet1.ncols):
            if sheet1.row_values(0)[i] == 'Result':
                vol = i
                break
        else:
            vol = sheet1.ncols + 1
        file_copy.get_sheet(0).write(row, vol, result)
        file_copy.get_sheet(0).col(0).width = 8000
        file_copy.get_sheet(0).col(1).width = 13000
        file_copy.get_sheet(0).col(2).width = 7000
        file_copy.save(self.result_path)


class ReadExcel:
    def __init__(self, file_path):
        self.file_path = file_path

    def read(self, row, col):
        file_open = xlrd.open_workbook(self.file_path)
        sheet1 = file_open.sheet_by_name('sheet1')
        if row >= sheet1.nrows or col >= sheet1.ncols:
            raise IOError('read excel failed:out of range')
        return sheet1.cell_value(row, col)

    def read_row(self, row):
        values = []
        file_open = xlrd.open_workbook(self.file_path)
        sheet1 = file_open.sheet_by_name('sheet1')
        if row >= sheet1.nrows:
            raise IOError('read excel failed:out of range')

        for col in range(sheet1.ncols):
            values.append(sheet1.cell_value(row, col))
        return values

    def read_col(self, col):
        values = []
        file_open = xlrd.open_workbook(self.file_path)
        sheet1 = file_open.sheet_by_name('sheet1')
        if col >= sheet1.ncols:
            raise IOError('read excel failed:out of range')

        for row in range(sheet1.nrows):
            values.append(sheet1.cell_value(row, col))
        return values
