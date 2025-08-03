# process_manager.py

import time
import threading
import random

from redis_handler import RedisClient
from proxy_utils import get_random_proxy
from ws_rest_worker import start_rest_worker, start_ws_worker
from logger_config import setup_logger

logger = setup_logger("process_manager")

def run_group_worker(group_id: int, coin_list: list[str], config: dict):
    logger.info(f"[GROUP {group_id}] Запуск процесса для {len(coin_list)} монет")

    redis_cfg = config["redis"]
    redis_client = RedisClient(
        host=redis_cfg["host"],
        port=redis_cfg["port"],
        db=redis_cfg["db"]
    )

    rest_proxy = get_random_proxy(config["proxy"]["rest_file"])
    ws_proxy = get_random_proxy(config["proxy"]["ws_file"])

    rest_interval = config["update"]["rest_interval_sec"]
    ws_attempts = config["update"]["max_ws_reconnect_attempts"]

    rest_thread = start_rest_worker(group_id, coin_list, redis_client, rest_proxy, rest_interval)

    depth = config["update"].get("orderbook_depth", 40)
    ws_thread = start_ws_worker(group_id, coin_list, redis_client, ws_proxy, ws_attempts, depth)

    rest_thread.join()
    ws_thread.join()