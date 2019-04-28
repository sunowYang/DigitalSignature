#! coding=utf8

import os
import xlrd
import xlwt
from xlutils.copy import copy


class Excel:
    def __init__(self, excel_path):
        self.excel_path = excel_path
        self._path, self._name = os.path.split(self.excel_path)

        if not self.excel_path.endswith('.xls') and not self.excel_path.endswith('.xlsx'):
            raise IOError('Parameter "excel_path" is not a excel path:%s' % self.excel_path)

    def create_new(self, sheet_name="Sheet1", title=None, *titles):
        if title is not None:
            titles = title
        if os.path.exists(self.excel_path):
            return self.excel_path

        if not os.path.exists(self._path):
            os.makedirs(self._path)
        elif os.path.isdir(self.excel_path):
            raise IOError('Method "create_new" needs a file path,not a dir path:%s' % self.excel_path)

        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet(sheet_name, cell_overwrite_ok=True)
        for index in range(len(titles)):
            sheet.write(0, index, titles[index])
        workbook.save(self.excel_path)
        return self.excel_path

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

    def set_col_width(self, sheet_name, **strings):
        pass

    # def set_col_fixed(self, col, sheet_name):
    #     workbook = xlrd.open_workbook(self.excel_path)
    #     workbook_copy = copy(workbook)
    #     sheet = workbook.sheet_by_name(sheet_name)
    #     sheet.
    #     workbook_copy.get_sheet(sheet_name).computed_column_width(col)
    #     workbook_copy.save(self.excel_path)


class WriteExcel(Excel):
    def __init__(self, excel_path, target_path=None):
        Excel.__init__(self, excel_path)
        self.target_path = target_path

    def check_if_exist(self):
        if not os.path.exists(self.excel_path):
            raise IOError('No found excel from path:%s' % self.excel_path)

    def write_cell(self, row, col, string, sheet_name="Sheet1"):
        self.check_if_exist()
        try:
            workbook = xlrd.open_workbook(self.excel_path)
            workbook_copy = copy(workbook)
            workbook_copy.get_sheet(sheet_name).write(row, col, string)
            if self.target_path:
                workbook_copy.save(self.target_path)
            else:
                workbook_copy.save(self.excel_path)
        except Exception, e:
            raise IOError('Write excel failed:%s' % e)

    def write_col(self, sheet_name, col, start_row=0, *strings):
        self.check_if_exist()
        try:
            workbook = xlrd.open_workbook(self.excel_path)
            workbook_copy = copy(workbook)
            for row in range(start_row, len(strings)):
                workbook_copy.get_sheet(sheet_name).write(row, col, strings[row-start_row])
            workbook_copy.save(self.excel_path)
        except Exception, e:
            raise IOError('Write excel failed:%s' % e)

    def write_row(self, row, sheet_name='Sheet1', start_col=0, *strings):
        self.check_if_exist()
        try:
            workbook = xlrd.open_workbook(self.excel_path)
            workbook_copy = copy(workbook)
            for col in range(start_col, len(strings)):
                workbook_copy.get_sheet(sheet_name).write(row, col, strings[col-start_col])
            if self.target_path:
                workbook_copy.save(self.target_path)
            else:
                workbook_copy.save(self.excel_path)
        except Exception, e:
            raise IOError('Write excel failed:%s' % e)

    def write_row_by_title(self, row, strings=None, sheet_name='Sheet1', **kwargs):
        """
            如果strings为空，那么使用不定长参数作为要写入的内容
        @param row:
        @param sheet_name:
        @type strings: dict
        """
        if strings is None:
            strings = kwargs
        self.check_if_exist()
        try:
            workbook = xlrd.open_workbook(self.excel_path)
            sheet = workbook.sheet_by_name(sheet_name)
            workbook_copy = copy(workbook)
            for key in strings.keys():
                for index in range(sheet.ncols):
                    if sheet.cell_value(0, index) == key:
                        col = index
                        break
                else:
                    raise IOError('No found col:%s when write excel' % key)
                workbook_copy.get_sheet(sheet_name).write(row, col, strings[key])
            if self.target_path:
                workbook_copy.save(self.target_path)
            else:
                workbook_copy.save(self.excel_path)
        except Exception, e:
            raise IOError('Write excel failed:%s' % e.message)

    def set_col_width(self, titles=None, sheet_name='Sheet1', **strings):
        self.check_if_exist()
        if titles is not strings:
            strings = titles
        try:
            workbook = xlrd.open_workbook(self.excel_path)
            sheet = workbook.sheet_by_name(sheet_name)
            workbook_copy = copy(workbook)
            for key in strings.keys():
                for index in range(sheet.ncols):
                    if sheet.cell_value(0, index) == key:
                        col = index
                        break
                else:
                    raise IOError('No found col:%s when write excel' % key)
                workbook_copy.get_sheet(sheet_name).col(col).width = strings[key]
            workbook_copy.save(self.excel_path)
        except Exception, e:
            raise IOError('Write excel failed:%s' % e)


class ReadExcel(Excel):
    def __init__(self, excel_path):
        Excel.__init__(self, excel_path)
        if not os.path.exists(self.excel_path):
            raise IOError('No found excel from path:%s' % self.excel_path)

    def read_cell(self, row, col, sheet_name='Sheet1'):
        sheet = xlrd.open_workbook(self.excel_path).sheet_by_name(sheet_name)
        return sheet.cell_value(row, col)

    def read_row(self, row, sheet_name='Sheet1'):
        values = []
        sheet = xlrd.open_workbook(self.excel_path).sheet_by_name(sheet_name)
        if row >= sheet.nrows:
            raise IOError('Read excel failed,the max row is %d,and given row: %d' % (sheet.nrows, row))

        for col in range(sheet.ncols):
            values.append(sheet.cell_value(row, col))
        return values

    def read_row_by_title(self, row, sheet_name='Sheet1', *titles):
        values = {}
        sheet = xlrd.open_workbook(self.excel_path).sheet_by_name(sheet_name)
        if row >= sheet.nrows:
            raise IOError('Read excel failed,the max row is %d,and given %d' % (sheet.nrows, row))

        for title in titles:
            for col in sheet.ncols:
                if sheet.cell_value(0, col) == title:
                    values[title] = sheet.cell_value(row, col)
                    break
            else:
                raise IOError('No found title:%s when read excel' % title)
        return values

    def read_col(self, col, sheet_name='Sheet1'):
        values = []
        sheet = xlrd.open_workbook(self.excel_path).sheet_by_name(sheet_name)
        if col >= sheet.ncols:
            raise IOError('Read excel failed,the max col is %d,and given col: %d' % (sheet.ncols, col))

        for row in range(sheet.nrows):
            values.append(sheet.cell_value(row, col))
        return values

    def read_col_by_count(self, col, rows, start_row=0, sheet_name='Sheet1'):
        values = []
        sheet = xlrd.open_workbook(self.excel_path).sheet_by_name(sheet_name)
        if col >= sheet.ncols:
            raise IOError('Read excel failed,the max col is %d,and given col:%d' % (sheet.ncols, col))
        if rows > sheet.nrows:
            raise IOError('Read excel failed,the max row is %d,and given rows: %d' % (sheet.ncols, col))
        elif rows+start_row > sheet.nrows:
            raise IOError('Read excel failed,the max row is %d,and given rows+start_row:%d' % (sheet.ncols, rows+start_row))

        for row in range(start_row, rows+start_row):
            values.append(sheet.cell_value(row, col))
        return values



if __name__ == '__main__':
    excel = WriteExcel(r'C:\Users\yuanbin\Desktop\123.xls')
    excel.write_cell(0, 2, 'abc1231111111111111111111111', sheet_name='abc123')
    excel.set_col_width('abc123', abc123=8888)
