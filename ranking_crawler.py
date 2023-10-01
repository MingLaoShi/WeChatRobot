import requests
from Util import send_msg_on_wechat
import time
import logging


class ranking_crawler:
    def __init__(self, logger, rank_num=10) -> None:
        self.logger = logger
        self.rank_num = rank_num
        self.header = header = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36 Edg/90.0.818.66"
        }
        self.craw_funcs = {
            ("帮助", "网站列表"): self.print_help,
            ("bilibili", "哔哩哔哩", "b站"): self.get_bili_rank,
        }

    def print_help(self, rank_num=10):
        print_str = ""
        for key, value in self.craw_funcs.items():
            print_str = print_str + str(key) + "\n"
        send_msg_on_wechat("排行榜", f"支持的参数:\n{print_str}")

    def get_bili_rank(self, rank_num=10):
        bili_url = "https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all"
        page = requests.get(bili_url, headers=self.header)
        if page.status_code == 200:
            self.logger.info("哔哩哔哩排行榜爬取成功。")
            data_json = page.json()
            rank_json = data_json.get("data").get("list")
            rank_str = ""
            rank_index = 0
            for vedio in rank_json:
                if rank_index >= rank_num:
                    break
                vedio_str = f"{rank_index}：{vedio.get('title')}（作者：{vedio.get('owner').get('name')}）\n"
                rank_str = rank_str + vedio_str
                rank_index = rank_index + 1
            send_msg_on_wechat("哔哩哔哩排行榜", rank_str)
        else:
            self.logger.warn(f"哔哩哔哩排行榜爬取失败！:{page.status_code}")
            send_msg_on_wechat("哔哩哔哩排行榜", "爬取失败！")

    def get_rank(self, web_name, rank_num=10):
        supported_websites = False
        for key, func in self.craw_funcs.items():
            if web_name[1] in key:
                supported_websites = True
                func(rank_num)
        if not supported_websites:
            send_msg_on_wechat("排行榜", "不支持的网站，可以让管理员进行添加！")


def test():
    time.sleep(1)
    ranking_crawler(logging).get_bili_rank()


if __name__ == "__main__":
    test()
