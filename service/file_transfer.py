import os
import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import QDir, QModelIndex
from PyQt5.QtWidgets import QFileSystemModel

import datetime
from crontab import CronTab

sys.path.append('E:/Workspaces/file_transfer/')
from convert.fm_file_transfer import Ui_MainWindow
from service.socket_client import connection_socket
from service.rw_file import checking_init_file_seting, update_file_setting
from service.thread_checking import ConnectionChecker


class FileTransfer(Ui_MainWindow):
    def __init__(self):
        self.model = None
        self.file_path_local_site = None

        self.setupUi(MainWindow)
        self.show_trv_path()
        self.trv_folder_local.clicked.connect(self.on_tree_view_clicked)

        host, server, port, username, password, local_site, remote_site, host_db, username_db, password_db, port_db, schema = checking_init_file_seting(
            file_path='E:/Workspaces/file_transfer/setting.json')

        self.show_config(host=host, server=server, port=port)
        self.start_connection_checker(server=server, port=port)
        self.btn_connect.clicked.connect(self.btn_connect_)

    def show_tb_file(self, file_path):
        self.model = QFileSystemModel()
        self.model.setRootPath('')
        self.tb_local.setModel(self.model)

        root_path = os.path.expanduser(file_path)
        root_index = self.model.index(root_path)
        self.tb_local.setRootIndex(root_index)

    def show_trv_path(self):
        self.model = QFileSystemModel()
        self.model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)
        self.model.setRootPath('')
        self.trv_folder_local.setModel(self.model)

    def on_tree_view_clicked(self, index: QModelIndex):
        self.file_path_local_site = self.model.filePath(index)
        self.txt_path_local.setPlainText(self.file_path_local_site)
        self.show_tb_file(self.file_path_local_site)

    def show_config(self, host, server, port):
        self.txt_host.setPlainText(host)
        self.txt_port.setPlainText(str(port))
        self.txt_server.setPlainText(server)

    def start_connection_checker(self, server, port):
        self.connection_checker = ConnectionChecker(server, port)
        self.connection_checker.connection_status.connect(self.update_status)
        self.connection_checker.start()

    def update_status(self, connected):
        color = "green" if connected else "red"
        self.lbl_checking.setStyleSheet(f"background-color: {color};")

    def btn_connect_(self):
        data = {
            "host": self.txt_host.toPlainText(),
            "server": self.txt_server.toPlainText(),
            "port": int(self.txt_port.toPlainText())
        }
        update_file_setting(file_setting='E:/Workspaces/file_transfer/setting.json', data=data)




if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = FileTransfer()

    MainWindow.show()
    sys.exit(app.exec_())
