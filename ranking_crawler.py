import requests
from Util import send_msg_on_wechat
import time
import logging
from bs4 import BeautifulSoup
import pickle

class ranking_crawler:
    def __init__(self, logger, rank_num=10) -> None:
        self.logger = logger
        self.rank_num = rank_num
        self.header = header = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36 Edg/90.0.818.66"
        }
        self.craw_funcs = {
            ("帮助", "网站列表"): self.print_help,
            ("bilibili", "哔哩哔哩", "b站","bl"): self.get_bili_rank,
            ("知乎","zh"): self.get_zhuhu_rank,
            ("贴吧","tb","粪坑"):self.get_tieba_rank,
            ("微博","wb"):self.get_weibo_rank,
            ("头条","今日头条","tt"):self.get_toutiao_rank,
            # ("抖音","dy"):self.get_douyin_rank
        }

    def print_help(self, rank_num=10):
        print_str = ""
        for key, value in self.craw_funcs.items():
            print_str = print_str + str(key) + "\n"
        send_msg_on_wechat("排行榜", f"支持的参数:\n{print_str}")

    def get_zhuhu_rank(self, rank_num=10):
        zhihu_url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=50&desktop=true"
        # selector_path = "#TopstoryContent > div > div.Topstory-hot.HotList.css-1x36n8t > div.HotList-list > section> div.HotItem-content > a > h2"
        page = requests.get(zhihu_url, headers=self.header)
        if page.status_code == 200:
            self.logger.info("知乎排行榜爬取成功。")
            page_json=page.json()
            rank_json=page_json.get('data')
            rank_str = ""
            rank_index = 1
            for d in rank_json:
                if rank_index>rank_num:
                    break
                rank = f"{rank_index}:{d.get('target').get('title')}\n"
                rank_str = rank_str + rank
                rank_index=rank_index+1
            send_msg_on_wechat("知乎排行榜", rank_str)
        else:
            self.logger.warn(f"知乎排行榜爬取失败{page.status_code}")
            send_msg_on_wechat("知乎排行榜", "爬取失败！")

    def get_tieba_rank(self, rank_num=10):
        tieba_url = "https://tieba.baidu.com/hottopic/browse/topicList?res_type=1"
        selector_path = "body > div.wrap1 > div > div.bang-bg > div > div.topic-body.clearfix > div.main > ul > li> div > div > a"
        page = requests.get(tieba_url, headers=self.header)
        if page.status_code == 200:
            self.logger.info("贴吧排行榜爬取成功。")
            page_text = page.text
            soup = BeautifulSoup(page_text, "lxml")
            data = soup.select(selector_path)
            rank_str = ""
            rank_index = 1
            for d in data:
                if rank_index>rank_num:
                    break
                rank = f"{rank_index}:{d.text}\n"
                rank_str = rank_str + rank
                rank_index=rank_index+1
            send_msg_on_wechat("贴吧排行榜", rank_str)
        else:
            self.logger.warn(f"贴吧排行榜爬取失败{page.status_code}")
        send_msg_on_wechat("贴吧排行榜", "爬取失败！")

    def get_bili_rank(self, rank_num=10):
        bili_url = "https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all"
        page = requests.get(bili_url, headers=self.header)
        if page.status_code == 200:
            self.logger.info("哔哩哔哩排行榜爬取成功。")
            data_json = page.json()
            rank_json = data_json.get("data").get("list")
            rank_str = ""
            rank_index = 1
            for vedio in rank_json:
                if rank_index > rank_num:
                    break
                vedio_str = f"{rank_index}：{vedio.get('title')}（作者：{vedio.get('owner').get('name')}）\n"
                rank_str = rank_str + vedio_str
                rank_index = rank_index + 1
            send_msg_on_wechat("哔哩哔哩排行榜", rank_str)
        else:
            self.logger.warn(f"哔哩哔哩排行榜爬取失败！:{page.status_code}")
            send_msg_on_wechat("哔哩哔哩排行榜", "爬取失败！")

    def get_weibo_rank(self,rank_num=10):
        weibo_url='https://weibo.com/ajax/statuses/topic_band?sid=v_weibopro&category=all&page=1&count=10'
        page=requests.get(weibo_url,headers=self.header)
        if page.status_code==200:
            self.logger.info("微博排行榜爬取成功。")
            data_json=page.json()
            rank_json=data_json.get('data').get('statuses')
            rank_str=''
            rank_index=1
            for row in rank_json:
                if rank_index>rank_num:
                    break
                rank_str=f"{rank_index}:{row.get('topic')}(讨论度：{row.get('mention')})\n"
            send_msg_on_wechat("微博排行榜",rank_str)
        else:
            self.logger.warn(f"微博排行榜爬取失败！{page.status_code}")
            send_msg_on_wechat("微博排行榜","爬取失败！")

    def get_toutiao_rank(self,rank_num=10):
        toutiao_url='https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc&_signature=_02B4Z6wo001019qA-QQAAIDCyt4cPSjgi9fapP2AAJPC2LrRUFbaiUBRvVQzj71AxNyPV05tlPJYvRT9-X3fNI7Ji6BLypaUf3gPz8b.GsfQlF25eqErGr7.4PVRy-uVZnUnSmeHMxCyXFOfb9'
        page=requests.get(toutiao_url,headers=self.header)
        if page.status_code==200:
            self.logger.info("头条排行榜爬取成功。")
            data_json=page.json()
            rank_json=data_json.get('data')
            rank_str=''
            rank_index=1
            for row in rank_json:
                if rank_index>rank_num:
                    break
                rank_str=f"{rank_index}:{row.get('title')}(热度：{row.get('HotValue')})\n"
            send_msg_on_wechat("头条排行榜",rank_str)
        else:
            self.logger.warn(f"头条排行榜爬取失败！{page.status_code}")
            send_msg_on_wechat("头条排行榜","爬取失败！")

    def get_douyin_rank(self,rank_num=10):
        douyin_url='https://www.douyin.com/aweme/v1/web/hot/search/list/?device_platform=webapp&aid=6383&channel=channel_pc_web&detail_list=1&source=6&pc_client_type=1&version_code=170400&version_name=17.4.0&cookie_enabled=true&screen_width=1920&screen_height=1080&browser_language=zh-CN&browser_platform=Win32&browser_name=Edge&browser_version=117.0.2045.43&browser_online=true&engine_name=Blink&engine_version=117.0.0.0&os_name=Windows&os_version=10&cpu_core_num=16&device_memory=8&platform=PC&downlink=10&effective_type=4g&round_trip_time=0&webid=7284997822021207593&msToken=T9V5nC80cSCjGV_EE1dRSMahHUFP-7w5X3AvX249yVjhuVdbuHzlF9V64UDIoBokipkEH8qRSwMGBoYj2jjEqr1hshqq4pb3Pz4FqW_a-ojT0GKe&X-Bogus=DFSzswVYrBUANVbUtOxZR2oB6lsu'
        # douyin_url='https://www.douyin.com/hot'
        response = requests.get('https://www.douyin.com/')
        cookies=response.cookies
        with open('cookies.pkl', 'wb') as f:
            pickle.dump(cookies, f)
        with open('cookies.pkl', 'rb') as f:
            cookies = pickle.load(f)
        header={
            'Cookie':';'.join([f'{cookie.name}={cookie.value}' for cookie in cookies])
        }
        page=requests.get(douyin_url,headers=header)
        if page.status_code==200:
            self.logger.info("抖音排行榜爬取成功。")
            data_json=page.json()
            rank_json=data_json.get('data').get('word_list')
            rank_str=''
            rank_index=1
            for row in rank_json:
                if rank_index>rank_num:
                    break
                rank_str=f"{rank_index}:{row.get('word')}\n"
            send_msg_on_wechat("抖音排行榜",rank_str)
        else:
            self.logger.warn(f"抖音排行榜爬取失败！{page.status_code}")
            send_msg_on_wechat("抖音排行榜","爬取失败！")

    def get_rank(self, web_name, rank_num=10):
        supported_websites = False
        for key, func in self.craw_funcs.items():
            if web_name[1] in key:
                supported_websites = True
                func(rank_num)
        if not supported_websites:
            send_msg_on_wechat("排行榜", "不支持的网站，可以让管理员进行添加！")


def test():
    ranking_crawler(logger=logging).get_douyin_rank()


if __name__ == "__main__":
    test()
