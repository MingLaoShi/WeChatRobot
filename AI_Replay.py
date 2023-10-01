from PIL import Image
from queue import Queue
import openai
from Util import (
    queue_limit_put,
    send_image_on_wechat,
    send_msg_on_wechat,
    dowanload_Image_From_Url,
)
from Util import Instrcutions


class AI_reply:
    def __init__(self, logger) -> None:
        self.api_key = (
            ""  # 换成你的openai api key
        )
        openai.api_key = self.api_key
        openai.proxy = "http://127.0.0.1:7890"  # 设置下代理，否则连不上网络
        self.model = "gpt-3.5-turbo"
        self.temperature = 0.7
        self.max_tokens = 200  # 设置200回复字数上限，担心我的额度啊
        self.n = 1
        self.msg_context = Queue()  # 保存的上下文
        self.msg_context_limit = 5  # 上下文大小，影响ai能记住几句之前的内容
        self.logger = logger

    # def test_api(self):
    #     messages = [{ "role": "user", "content": '欢迎使用openai！' }]
    #     model = 'gpt-3.5-turbo'
    #     response = openai.ChatCompletion.create(
    #         model=model,
    #         messages=messages,
    #         temperature=self.temperature,
    #         n=self.n
    #     )
    #     queue_limit_put(self.msg_context,self.msg_context_limit,response.choices[0].message)
    #     if __debug__:
    #         print(f'\033[31m收到的数据:{response.choices[0].message.content}\033[0m')

    # 制作消息放入上下文中
    def create_message(self, content):
        message = {"role": "user", "content": content}
        queue_limit_put(self.msg_context, self.msg_context_limit, message)
        return self.msg_context

    # 请求api，获得返回结果
    def get_response(self, message):
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=message,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
        except openai.APIConnectionError as e:
            self.logger.error(e)
            return ("error", "网络又抽风了，这也是没办法的事。😢😢😢")

        queue_limit_put(
            self.msg_context, self.msg_context_limit, response.choices[0].message
        )  # 将返回的结果放入上下文中，让ai能记住说了什么
        self.logger.info(f"从openai获得回复：{response.choices[0].message.content}")
        return ("success", response.choices[0].message.content)

    def chat_to_ai(self, msg):
        text = msg[1]
        self.create_message(text)
        self.logger.info(f"token:{list(self.msg_context.queue)}")
        (statue, res) = self.get_response(list(self.msg_context.queue))
        if statue == "success":
            send_msg_on_wechat(msg, res)
        elif statue == "error":
            send_msg_on_wechat("链接不上openai了", res)

    def generate_image_ai(self, msg):
        text = msg[1]
        response = openai.Image.create(
            prompt=text, n=1, size="512x512", response_format="url"
        )
        url = response.data[0].url
        filepath = dowanload_Image_From_Url(url, "aiImage")
        # filepath="aiImage\\2055f946-cf92-4a9f-9c7c-de5cba67b4a1.png"F
        if filepath != "error":
            self.logger.info(f"从{url}保存图片：{filepath}")
            image = Image.open(filepath)
            send_image_on_wechat(msg, image)
        else:
            self.logger.warn(f"图片下载失败：{url}")

    def analyze_instructions(self, instrcution):
        operation = instrcution[0]
        message = instrcution[1]
        cases = {
            Instrcutions.CHAT: lambda: self.chat_to_ai(message),
            Instrcutions.CREATE_IMAGE: lambda: self.generate_image_ai(message),
        }
        cases.get(operation, lambda: None)()

    # def run(self):
    # while True:
    #     self.logger.info("等待新消息。")
    #     msg = self.queue.get()
    #     self.logger.info(f"获得新消息，正在请求openai：{msg}")
    #     # self.create_message(msg)
    #     # logger.info(f"token:{list(self.msg_context.queue)}")
    #     # (statue,res)=self.get_response(list(self.msg_context.queue))
    #     # if statue=='success':
    #     #     self.send_msg_on_wechat(msg,res)
    #     # elif statue=='error':
    #     #     self.send_msg_on_wechat('链接不上openai了',res)
    #     self.analyze_instructions(msg)
