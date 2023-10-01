from Util import Instrcutions
from AI_Replay import AI_reply
from Ranking_Crawler import ranking_crawler
from Generate_qrcode import generate_qrcode
from Emoji_Synthesis import emoji_synthesis
class robot_route:
    def __init__(self, queue, logger) -> None:
        self.queue = queue
        self.logger = logger
        self.ai_replay = AI_reply(logger)
        self.msg = ""
        self.routes = {
            Instrcutions.CHAT: self.ai_replay.chat_to_ai,
            Instrcutions.CREATE_IMAGE: self.ai_replay.generate_image_ai,
            Instrcutions.RANK_CRAWLER: self.rank_crawler_route,
            Instrcutions.GEN_QRCODE:self.generate_qrcode_route,
            Instrcutions.EMOJI_SYN:self.emoji_syn_route,
        }

    def emoji_syn_route(self,msg):
        es=emoji_synthesis(self.logger)
        es.synthesis(msg)

    def rank_crawler_route(self, msg):
        rc = ranking_crawler(self.logger)
        rc.get_rank(msg)

    def generate_qrcode_route(self,msg):
        gq=generate_qrcode(self.logger)
        gq.generate(msg)

    def run(self):
        while True:
            self.logger.info("等待新消息。")
            instruct, self.msg = self.queue.get()
            self.logger.info(f"获得新消息，跳转路由：{self.msg}。")
            self.routes.get(instruct)(self.msg)
