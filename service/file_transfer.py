import os
import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import QDir, QModelIndex
from PyQt5.QtWidgets import QFileSystemModel
import threading

import datetime
from crontab import CronTab

current_dir = os.path.abspath(os.path.dirname(__file__))
PATH = os.path.abspath(os.path.join(current_dir, '..'))
print(PATH)

sys.path.append(PATH)
from convert.fm_file_transfer import Ui_MainWindow
from service.rw_file import checking_init_file_setting, update_file_setting, reading_file_setting
from service.thread_checking import ConnectionChecker
from service.transfer_threading import DirectoryMonitorThread
from service.transfer_threading import TransferThread
from service.socket_client import ConnectionSocket


class FileTransfer(Ui_MainWindow):
    def __init__(self):
        self.monitor_dir = None
        self.model = None
        self.file_path_local_site = None
        self.host = None
        self.server = None
        self.port = None
        self.local_site = None

        self.setupUi(MainWindow)
        self.show_trv_path()
        self.trv_folder_local.clicked.connect(self.on_tree_view_clicked)
        self.btn_connect.clicked.connect(self.btn_connect_)
        self.btn_confirm.clicked.connect(self.btn_confirm_)

        self.host, self.server, self.port, username, password, self.local_site, remote_site, host_db, username_db, password_db, port_db, schema = checking_init_file_setting(
            file_path=PATH + '/setting.json')

        self.show_config(host=self.host, server=self.server, port=self.port)
        # self.start_connection_checker(server=self.server, port=self.port)

        # 
        # self.transfer_file(dir=self.local_site)

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
        update_file_setting(file_setting=PATH + '/setting.json', data=data)
        self.connection_checker.stop()
        self.host = None
        self.server = None
        self.port = None

        self.host, self.server, self.port, username, password, local_site, remote_site, host_db, username_db, password_db, port_db, schema = reading_file_setting(
            file_setting=PATH + '/setting.json')
        self.start_connection_checker(server=self.server, port=self.port)

    def transfer_file(self, dir):
        self.monitor_dir = DirectoryMonitorThread(directory=dir, host=self.host, port=self.port)
        self.monitor_dir.start()
        print(f"Directory file : {dir}")

    def btn_confirm_(self):
        data = {
            "local_site": self.txt_path_local.toPlainText()
        }
        update_file_setting(file_setting=PATH + '/setting.json', data=data)
        _, _, _, _, _, self.file_path_local_site, _, _, _, _, port_db, schema = reading_file_setting(
            file_setting=PATH + '/setting.json')
        print(f"Confirm path local: {self.file_path_local_site}")

        self.send_file_exists(directory=self.local_site, host=self.host, port=self.port)



    def send_file_exists(self, directory, host, port):
        threads = []
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                # thread = threading.Thread(target=self.send_file_(host=host, port=port,file=file_path))
                # thread.start()
                # threads.append(thread)
                
                connection = ConnectionSocket(host=host, port=port)
                sock = connection.connect_socket()
                connection.send_file(sock=sock, file_path=file_path)
        # for thread in threads:
        #     thread.join()

    def send_file_(host, port, file):
        connection = ConnectionSocket(host=host, port=port)
        sock = connection.connect_socket()
        connection.send_file(sock=sock, file_path=file)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = FileTransfer()

    MainWindow.show()
    sys.exit(app.exec_())
