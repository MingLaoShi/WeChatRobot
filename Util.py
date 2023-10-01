import pyautogui
from pyperclip import copy
import requests
import uuid
import os
import io
import win32clipboard
from enum import Enum


class Instrcutions(Enum):
    CHAT = "%小马"
    CREATE_IMAGE = "%图片"
    COUNTDOWN = "%倒计时"
    RANK_CRAWLER = "%排行榜"


def print_help():
    help = (
        f"支持的指令：\n"
        f"{Instrcutions.CHAT.value} 对话消息：智能AI聊天\n"
        f"{Instrcutions.CREATE_IMAGE.value} 图片描述：生成AI图片\n"
        f"{Instrcutions.COUNTDOWN.value} 时间：开始倒计时,没做好呢别乱用！\n"
        f"{Instrcutions.RANK_CRAWLER.value} 网站名：爬取网站排行榜。\n"
        f"注意：如果同一个人在机器人未回复第一条消息时发送相同的第二条消息，机器人是无法识别第二条消息的。这是机器人实现方式本身的缺陷，不是bug！"
    )
    return help


def queue_limit_put(queue, limit, item):
    queue.put(item)
    if queue.qsize() > limit:
        queue.get()


# 添加@功能在之后
def send_msg_on_wechat(message, response):
    send_msg = ""
    if type(message) == tuple:
        send_msg = f"{message[0]}问{message[1]}\n---------\n{response}"
    else:
        send_msg = f"{message}\n---------\n{response}"
    copy(send_msg)
    pyautogui.hotkey("ctrl", "v")
    pyautogui.hotkey("alt", "s")


# 添加@功能在之后
def send_image_on_wechat(message, image):
    if type(message) == tuple:
        copy(message[1])
    else:
        copy(message)
    pyautogui.hotkey("ctrl", "v")
    win32clipboard.OpenClipboard()
    try:
        output = io.BytesIO()
        image.save(output, "BMP")
        data = output.getvalue()[14:]
        output.close()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    finally:
        win32clipboard.CloseClipboard()
        pyautogui.hotkey("ctrl", "v")
    pyautogui.hotkey("alt", "s")


def dowanload_Image_From_Url(url, path, filename=None):
    if filename is None:
        filename = str(uuid.uuid4()) + ".png"
    file_path = os.path.join(path, filename)
    image = requests.get(url)
    if image.status_code == 200:
        with open(file_path, "wb") as file:
            file.write(image.content)
        print(f"{filename}下载完成！")
        return file_path
    else:
        print(f"图片加载失败！[{image.status_code}]")
        return "error"
