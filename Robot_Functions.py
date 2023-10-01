from Util import send_msg_on_wechat
import time
import re


websit_dict = {
    "https://www.bilibili.com/": ["哔哩哔哩"],
    "https://www.zhihu.com/": ["知乎"],
    "https://www.csdn.net/": ["csdn", "CSDN"],
    "https://tieba.baidu.com/hottopic/browse/topicList?res_type=1": ["贴吧"],
}


class local_function:
    def __init__(self, logger) -> None:
        self.logger = logger

    # 倒计时功能，未完成
    def countdown(self, duration):
        try:
            matches = re.findall(r"\d+小时", duration)

            units = duration.split("小时")[0].split("分") + duration.split("分")[1].split(
                "秒"
            )
            time_values = [int(unit) for unit in units]
        except Exception as e:
            send_msg_on_wechat("倒计时格式不正确！", f"{duration}\n正确的格式为xx小时xx分xx秒！")
        send_msg_on_wechat(f"倒计时{duration}秒", "开始倒计时！")
        time.sleep(duration)
        send_msg_on_wechat(f"倒计时{duration}秒", "倒计时结束！")
