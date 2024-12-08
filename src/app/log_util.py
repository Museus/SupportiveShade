import logging
# from logging_loki import LokiQueueHandler
# from multiprocessing import Queue
# import os

# loki_handler = LokiQueueHandler(
#     Queue(-1),
#     url=f"{os.getenv("LOKI_SERVER")}/loki/api/v1/push",
#     tags={"application": "supportive_shade"},
#     auth=(os.getenv("LOKI_USERNAME"), os.getenv("LOKI_PASSWORD")),
#     version="1",
# )

logger = logging.getLogger("discord")
# logger.addHandler(loki_handler)
