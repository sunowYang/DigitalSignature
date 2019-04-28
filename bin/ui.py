#! coding=utf-8

import os
import sys
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from Config import Config
from style import STYLE
from start import Run
import threading

# ********************************Get executing path******************************
if getattr(sys, 'frozen', False):
    BASE_PATH = os.path.dirname(sys.executable)
else:
    BASE_PATH = os.path.dirname(__file__)


# ********************************************************************************


class MainWindow(QDialog):
    def __init__(self, log, base_path, data=None, parent=None):
        super(MainWindow, self).__init__(parent)
        self.log = log
        self.base_path = base_path
        self.run = Run(base_path)

        # 界面设置
        self.setStyleSheet(STYLE)
        self.resize(600, 450)
        self.setWindowTitle('数字签名')
        # 界面控件定义
        self.checkbox_compare = QCheckBox('对比两个版本数字签名')
        self.edit_source = QLineEdit()
        self.btn_source_file_browse = QPushButton('浏 览')

        self.label_compare = QLabel('请选择新版本的安装包：')
        self.edit_compare = QLineEdit()
        self.btn_compare_file_browse = QPushButton('浏 览')

        self.checkbox_filter = QCheckBox('过滤文件:')
        self.edit_filter = QLineEdit()

        self.text_edit_log = QTextEdit()
        self.process_bar = QProgressBar()
        self.process_bar.setVisible(False)
        self.process_bar.setAlignment(Qt.AlignCenter)

        self.proceed_btn = QPushButton('执 行')
        self.exit_btn = QPushButton('退 出')

        # 初始化控件值
        if data and isinstance(data, dict):
            self.edit_source.setText(data['source'] if 'source' in data.keys() else None)
            self.edit_compare.setText(data['compare_source'] if 'compare_source' in data.keys() else None)

            if 'compare' in data.keys():
                self.checkbox_compare.setChecked(True)
            if 'filter' in data.keys():
                self.checkbox_filter.setChecked(True)
                self.edit_filter.setText(data['filter'])
        # 界面控件布局
        self.ui()
        self.checkbox_compare_click()
        self.checkbox_filter_click()

    def ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.checkbox_compare)
        main_layout.addWidget(QLabel('请选择安装包：'))
        main_layout.addLayout(self.source_layout())
        main_layout.addWidget(self.label_compare)
        main_layout.addLayout(self.compare_layout())
        main_layout.addLayout(self.filter_layout())

        main_layout.addWidget(self.text_edit_log)
        main_layout.addWidget(self.process_bar)
        main_layout.addLayout(self.proceed_layout())

        # 信号
        self.checkbox_compare.clicked.connect(self.checkbox_compare_click)
        self.btn_source_file_browse.clicked.connect(self.source_btn_file_click)
        self.btn_compare_file_browse.clicked.connect(self.compare_btn_click)
        self.checkbox_filter.clicked.connect(self.checkbox_filter_click)
        self.proceed_btn.clicked.connect(self.proceed)
        self.exit_btn.clicked.connect(self.close)
        self.run.progress_signal.connect(self.update_ui)

    def checkbox_compare_click(self):
        if self.checkbox_compare.isChecked():
            self.label_compare.setHidden(False)
            self.edit_compare.setHidden(False)
            self.btn_compare_file_browse.setHidden(False)
        else:
            self.label_compare.setHidden(True)
            self.edit_compare.setHidden(True)
            self.btn_compare_file_browse.setHidden(True)

    def source_btn_file_click(self):
        file_name, file_type = QFileDialog.getOpenFileName(self, '选择源文件', './', '*.exe')
        self.edit_source.setText(file_name)

    def compare_btn_click(self):
        file_name, file_type = QFileDialog.getOpenFileName(self, '选择对比文件', './', '*.exe')
        self.edit_compare.setText(file_name)

    def checkbox_filter_click(self):
        if self.checkbox_filter.isChecked():
            self.edit_filter.setEnabled(True)
        else:
            self.edit_filter.setEnabled(False)

    def proceed(self):
        try:
            self.text_edit_log.clear()
            self.proceed_btn.setEnabled(False)
            self.process_bar.setHidden(False)
            self.update_ui(1, '初始化中...')
            data = self.save()
            thread1 = threading.Thread(target=self.run.start, args=(data, ))
            thread1.start()
        except Exception, e:
            QMessageBox.warning(self, '警告', e.message)

    def save(self):
        data = {}
        # 获取参数
        if self.checkbox_compare.isChecked():
            data['compare'] = '1'
            data['compare_source'] = self.edit_compare.text()
            if not os.path.exists(self.edit_compare.text()):
                raise IOError('对比安装包不存在，请重新选择')
        if self.checkbox_filter.isChecked():
            data['filter'] = self.edit_filter.text()
        data['source'] = self.edit_source.text()

        # 检查参数
        if not os.path.exists(self.edit_source.text()):
            raise IOError('安装包不存在，请重新选择')

        # 两个安装包名称不能一样
        if os.path.split(self.edit_source.text())[1] == os.path.split(self.edit_compare.text())[1]:
            raise IOError('两个安装包的名称不能一样，请修改后重试')
        if not os.path.exists(os.path.join(self.base_path, 'config')):
            os.mkdir(os.path.join(self.base_path, 'config'))
        config_path = os.path.join(self.base_path, 'config', 'config.ini')
        Config(self.log, config_path).write(data)
        return data

    def update_ui(self, progress, string):
        """
            写日志、界面日志、执行进度
        @param progress: int-执行进度
        @param string: str-显示日志
        """
        if progress >= 100:
            progress = 100
            self.log.logger.error(string)
            self.proceed_btn.setEnabled(True)
        else:
            self.log.logger.info(string)
        self.text_edit_log.append(string)
        self.process_bar.setValue(progress)


    def source_layout(self):
        layout = QHBoxLayout()
        layout.addWidget(self.edit_source, 5)
        layout.addWidget(self.btn_source_file_browse, 1)
        return layout

    def compare_layout(self):
        layout = QHBoxLayout()
        layout.addWidget(self.edit_compare, 5)
        layout.addWidget(self.btn_compare_file_browse, 1)
        return layout

    def filter_layout(self):
        layout = QHBoxLayout()
        layout.addWidget(self.checkbox_filter)
        layout.addWidget(self.edit_filter)
        return layout

    def proceed_layout(self):
        layout = QHBoxLayout()
        layout.addStretch(1)
        layout.addWidget(self.proceed_btn)
        layout.addWidget(self.exit_btn)
        return layout


def run(log, base_path):
    config_path = os.path.join(base_path, 'config', 'config.ini')
    data = Config(log, config_path).read() if os.path.exists(config_path) else None

    app = QApplication(sys.argv)
    ft = QFont()
    ft.setPointSize(11)
    ft.setFamily("宋体")
    app.setFont(ft)

    main_window = MainWindow(log, base_path, data)
    main_window.show()
    sys.exit(app.exec_())
