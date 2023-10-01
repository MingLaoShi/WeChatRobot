import pyautogui
from PIL import ImageChops
import time
from cnocr import CnOcr
from queue import Queue
import threading
import logging
from Util import send_msg_on_wechat, Instrcutions, print_help
import Robot_Functions
from WeChatPanelControl import WeCahtPanelControl
from Funs_Route import robot_route


class WeChatRobot:
    def __init__(self, logger) -> None:
        self.snap_position = [300, 60, 980, 825]  # 截图框的位置：left,top,length,height
        self.dialog_left = 340  # 消息框的左边界
        self.ocr = CnOcr()
        self.message_list = Queue()  # 新消息队列
        self.robot_name = "%小马"
        self.using_name = True  # True时要带机器人名字的消息才会回复，False所有消息都回复
        self.snap_error_check = True
        self.logger = logger
        self.local_funs = Robot_Functions.local_function(logger)
        self.panel_control = WeCahtPanelControl(logger)

    """
    对屏幕区域进行截图
    args:
        x,y:左上点的坐标
        m:长度
        n:高度
    """

    def snap(self, x, y, m, n):
        try:
            im = pyautogui.screenshot(region=(x, y, m, n))
            self.snap_error_check = True
        except Exception as e:
            if self.snap_error_check:
                self.snap_error_check = False  # 防止发送太多的崩溃消息
                send_msg_on_wechat("我崩溃啦！！！😥", "截图失败了，怎么回事。快让马铭去修！")
        return im

    # 对比两张图片相似度
    def compare_image(self, screenshot1, screenshot2):
        image1 = screenshot1
        image2 = screenshot2
        diff = ImageChops.difference(image1, image2)
        diff_image = diff.convert("RGBA")
        diff_count = diff.getbbox()
        if diff_count is None:  # 与上一张截图相同
            return False
        similarity = 1 - (
            (diff_count[2] - diff_count[0]) * (diff_count[3] - diff_count[1])
        ) / (image1.width * image1.height)
        if __debug__:
            print(f"相似度：{similarity}")
        if similarity >= 0.95:  # 相似度大于0.95判定为相同，低于0.95判定为有新消息
            return False
        return True

    # 寻找对话框的坐下点坐标
    def find_dialog_leftbott(self, im):
        x = 80
        y = self.snap_position[3] - 1
        while y > 0:
            if im.getpixel((x, y)) == (255, 255, 255):
                return (x, y)
            else:
                y = y - 1
        return (-1, -1)

    # 寻找对话框的长与高，(x,y)为左下点坐标
    def find_dialog_lenhei(self, im, x, y):
        right = x
        top = y
        while right < self.snap_position[2]:
            if im.getpixel((right, y)) != (255, 255, 255):
                break
            right = right + 1
        while top > 0:
            if im.getpixel((x, top)) != (255, 255, 255):
                break
            top = top - 1
        if right == self.snap_position[2] or top == 0:
            return (-1, -1)
        return (right - x, y - top)

    # def test_ai_reply(self):
    #     time.sleep(1)
    #     for i in range(2):
    #         self.message_list.put(f"你是谁")
    def analyze_instructions(self, msg):
        text = msg[1]
        text = text.replace(" ", "")
        if text is None or text == "":
            return
        if self.using_name and text.startswith(self.robot_name):
            text = text.replace(self.robot_name, "")  # 识别出机器人名字，然后从消息中去除机器人名字
            self.message_list.put((Instrcutions.CHAT, (msg[0], text)))
        elif text[0] == "%":
            if text.startswith(Instrcutions.CREATE_IMAGE.value):
                text = text.replace(Instrcutions.CREATE_IMAGE.value, "")
                self.message_list.put((Instrcutions.CREATE_IMAGE, (msg[0], text)))
            elif text.startswith(Instrcutions.COUNTDOWN.value):
                text = text.replace(Instrcutions.COUNTDOWN.value, "")
                self.message_list.put((Instrcutions.COUNTDOWN, (msg[0], text)))
            elif text.startswith(Instrcutions.RANK_CRAWLER.value):
                text = text.replace(Instrcutions.RANK_CRAWLER.value, "")
                self.message_list.put((Instrcutions.RANK_CRAWLER, (msg[0], text)))
            elif text.startswith(Instrcutions.GEN_QRCODE.value):
                text = text.replace(Instrcutions.GEN_QRCODE.value, "")
                self.message_list.put((Instrcutions.GEN_QRCODE, (msg[0], text)))
            elif text.startswith(Instrcutions.EMOJI_SYN.value):
                text = text.replace(Instrcutions.EMOJI_SYN.value, "")
                self.message_list.put((Instrcutions.EMOJI_SYN, (msg[0], text)))
            else:
                send_msg_on_wechat("未知指令！", print_help())
        elif not self.using_name:
            self.message_list.put((Instrcutions.CHAT, (msg[0], text)))
        else:
            pass

    def run(self):
        privous_screenshot = None
        time.sleep(5)  # 等我切换到微信页面(┬┬﹏┬┬)
        while True:
            # 对微信界面进行截图作为原始图
            im = self.snap(
                self.snap_position[0],
                self.snap_position[1],
                self.snap_position[2],
                self.snap_position[3],
            )
            # 寻找消息框并截图
            (dialog_x, dialog_y) = self.find_dialog_leftbott(im)
            if dialog_x == -1 or dialog_y == -1:
                self.logger.warning("查找对话框位置失败!")
                continue
            if __debug__:
                print(f"dialog_x,dialog_y:{dialog_x,dialog_y}")
            (dialog_len, dialog_hei) = self.find_dialog_lenhei(im, dialog_x, dialog_y)
            if dialog_len == -1 or dialog_hei == -1:
                self.logger.warning("查找对话框长宽失败！")
                continue
            if __debug__:
                print(f"dialog_len,dialog_hei{dialog_len,dialog_hei}")
            # 根据获得的参数截取对话框的图片
            dialog_image = im.crop(
                (dialog_x, dialog_y - dialog_hei, dialog_x + dialog_len, dialog_y)
            )

            hasNews = False
            if privous_screenshot is not None:
                # 与上一张截图进行对比，相似度是否在阈值内
                # 此处只对比了消息框的内容，会导致用户连续发送相同的内容不会认为其是新消息，暂时没解决办法
                hasNews = self.compare_image(privous_screenshot, dialog_image)
            if hasNews:
                # 使用cnocr进行识别，部分文字仍识别不正确，但正确率仍可以接受
                result = self.ocr.ocr(dialog_image)
                res_text = ""
                for element in result:  # 拼接识别的文字
                    res_text = res_text + element.get("text")
                self.logger.info(f"识别新消息：{res_text}")
                # if self.using_name:
                self.analyze_instructions(res_text)
                # if res_text.startswith(self.robot_name):
                #     res_text=res_text.replace(self.robot_name,"")#识别出机器人名字，然后从消息中去除机器人名字
                #     self.message_list.put(res_text)
                # else:
                #         self.message_list.put(res_text)

            privous_screenshot = dialog_image
            time.sleep(0.5)

    def check_new_message(self, previous_msg):
        current_list = self.panel_control.get_chat_list(self.panel_control.chat_panel)
        current_msg = self.panel_control.get_message_from_panel(current_list[-1])
        if current_msg[0] != "" and current_msg != previous_msg:
            self.logger.info(f"有新消息:{self.panel_control.get_message_from_panel(current_list[-1])}")
            previous_msg = current_msg
            return (True, current_msg)
        return (False, current_msg)

    def new_run(self):
        previous_msg = self.panel_control.get_message_from_panel(
            self.panel_control.get_chat_list(self.panel_control.chat_panel)[-1]
        )
        while True:
            has_new_msg = False
            has_new_msg, previous_msg = self.check_new_message(previous_msg)
            if has_new_msg and previous_msg[0]!='马老师':
                self.analyze_instructions(previous_msg)
            time.sleep(0.5)


def test():
    robot = WeChatRobot(logging)
    robot.new_run()


def main():
    logger = logging.getLogger("robot_logger")
    logger.setLevel("INFO")
    file_handler = logging.FileHandler("log\\robot.txt")
    file_handler.setLevel("INFO")
    fmt = logging.Formatter(
        "%(filename)s-%(lineno)d-%(asctime)s-%(levelname)s-%(message)s"
    )
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)
    logger.info("开始运行！")
    robot = WeChatRobot(logger=logger)
    route = robot_route(robot.message_list, logger)
    # ai=AI_reply(queue=robot.message_list,logger=logger)
    logger.info("初始化完成")
    # 创建线程监控是否有新消息，然后请求api
    thread = threading.Thread(target=route.run)
    thread.start()
    robot.new_run()
    thread.join()
    logger.info("运行结束！")


if __name__ == "__main__":
    main()
    # test()
