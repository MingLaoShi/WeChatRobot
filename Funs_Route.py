from Util import Instrcutions
from AI_Replay import AI_reply
from ranking_crawler import ranking_crawler


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
        }

    def rank_crawler_route(self, msg):
        rc = ranking_crawler(self.logger)
        rc.get_rank(msg)

    def run(self):
        while True:
            self.logger.info("等待新消息。")
            instruct, self.msg = self.queue.get()
            self.logger.info(f"获得新消息，跳转路由：{self.msg}。")
            self.routes.get(instruct)(self.msg)
