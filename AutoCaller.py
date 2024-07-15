from pywinauto.application import Application
import configparser
import os
import time
import tkinter as tk
from tkinter import simpledialog

root = tk.Tk()
root.withdraw()
phone_number = simpledialog.askstring(
    "輸入", "請輸入要撥打的電話號碼（例如：'123456789'）:")
app = Application(backend="win32").connect(
    title=phone_number, timeout=10)

window = app.window(title=phone_number)
dial_button = window.child_window(
    title="撥號", control_id=int('03FF', 16))
end_call_button = window.child_window(
    title="End", control_id=int('041F', 16))
config_path = os.path.expanduser('~\\AppData\\Roaming\\MicroSIP\\MicroSIP.ini')


def check_last_call_status(config_path):
    config = configparser.ConfigParser()
    config.read(config_path, encoding='utf-16')
    calls_keys = config.options('Calls')
    last_call_key = calls_keys[-1]
    last_call_value = config.get('Calls', last_call_key)
    status, duration = last_call_value.split(
        ';')[-1], int(last_call_value.split(';')[4])
    return status, duration


def wait_and_check(config_path, last_modified_time, wait_time):
    time.sleep(wait_time)
    current_modified_time = os.path.getmtime(config_path)
    if current_modified_time == last_modified_time:
        return 'ongoing'
    else:
        status, duration = check_last_call_status(config_path)
        if status == '' and duration == 0:
            return 'ongoing'
        elif status in ['取消', '無法提供服務', '忙線中', 'Server Failure: 503 無法提供服務']:
            return 'retry'
        elif status == '掛斷' and duration < 20:
            return 'retry'
        elif status == '掛斷' and duration >= 30:
            return 'answered'


def auto_call_until_answered(dial_button, end_call_button, config_path):
    last_modified_time = os.path.getmtime(config_path)

    while True:
        dial_button.click()
        for wait_time in [2, 5, 7, 10, 12, 14, 16, 20, 25, 30]:
            result = wait_and_check(config_path, last_modified_time, wait_time)
            if result == 'retry':
                break  # 跳出for loop，重新while loop
            elif result == 'answered':
                print('電話已接通。')
                return  # 結束函數
            elif result == 'ongoing':
                continue  # 繼續for loop


auto_call_until_answered(dial_button, end_call_button, config_path)
