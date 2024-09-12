import json
import os

def reading_file_setting(file_setting):

    try:
        with open(file_setting, 'r') as f:
            settings = json.load(f)

        host = settings.get("host", "")
        server = settings.get("server", "")
        port = settings.get("port", "")
        username = settings.get("username", "admin")
        password = settings.get("password", "admin")
        local_site = settings.get("local_site", "")
        remote_site = settings.get("remote_site", "")

        database = settings.get("database", {})
        host_db = database.get("host_db", "")
        username_db = database.get("username_db", "")
        password_db = database.get("password_db", "")
        port_db = database.get("port_db", "")
        schema = database.get("schema", "")

        print(f"Host: {host}")

        return host, server, port, username, password, local_site, remote_site, host_db, username_db, password_db, port_db, schema

    except FileNotFoundError:
        print(f"Không tìm thấy file: {file_setting}")
        return False
    except json.JSONDecodeError:
        print("Lỗi khi đọc file JSON")
        return False


def write_file_setting(file_setting):
    settings = {
                "host": "127.0.0.1",
                "server": "192.168.1.1",
                "port": 80,
                "username": "admin",
                "password": "admin",
                "local_site": "",
                "remote_site": "",
                "database": {
                    "host_db": "",
                    "username_db": "",
                    "password_db": "",
                    "port_db": "",
                    "schema": ""
                }
            }

    host = settings['host']
    server = settings['server']
    port = settings['port']
    username = settings['username']
    password = settings['password']
    local_site = settings['local_site']
    remote_site = settings['remote_site']

    host_db = settings['database']['host_db']
    username_db = settings['database']['username_db']
    password_db = settings['database']['password_db']
    port_db = settings['database']['port_db']
    schema = settings['database']['schema']

    try:
        with open(file_setting, 'w') as f:
            json.dump(settings, f, indent=4)
        print(f"Đã ghi file thành công vào {file_setting}")
    except IOError:
        print("Lỗi khi ghi file")

    return host, server, port, username, password, local_site, remote_site, host_db, username_db, password_db, port_db, schema

def is_exist_file(file_path):
    return os.path.isfile(file_path)


def checking_init_file_setting(file_path):
    if is_exist_file(file_path=file_path):
        return reading_file_setting(file_setting=file_path)
    else:
       return write_file_setting(file_path)
    
def update_file_setting(file_setting, data):
    try:
        with open(file_setting, 'r') as f:
            settings = json.load(f)

        settings.update(data)
        with open(file_setting, 'w') as f:
            json.dump(settings, f, indent=4)

        print(f"Đã cập nhật thành công file: {file_setting}")

    except FileNotFoundError:
        print(f"Không tìm thấy file: {file_setting}")
    except json.JSONDecodeError:
        print("Lỗi khi đọc hoặc ghi file JSON")
    