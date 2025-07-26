# process_manager.py

import time
import threading
import random

from redis_handler import RedisClient
from proxy_utils import get_random_proxy

# Здесь будут импорты WebSocket/REST логики, пока заглушки
# from ws_rest_worker import start_ws, start_rest

def run_group_worker(group_id: int, coin_list: list[str], config: dict):
    print(f"[GROUP {group_id}] Запуск процесса для {len(coin_list)} монет")

    # Redis init
    redis_cfg = config["redis"]
    redis_client = RedisClient(
        host=redis_cfg["host"],
        port=redis_cfg["port"],
        db=redis_cfg["db"]
    )

    # Получаем прокси
    rest_proxy = get_random_proxy(config["proxy"]["rest_file"])
    ws_proxy = get_random_proxy(config["proxy"]["ws_file"])

    # Параметры обновлений
    rest_interval = config["update"]["rest_interval_sec"]
    ws_attempts = config["update"]["max_ws_reconnect_attempts"]

    # Пример заглушки логики
    def rest_thread():
        while True:
            for coin in coin_list:
                # Здесь будет вызов реального REST-запроса
                print(f"[REST-{group_id}] {coin}: обновление через REST")
                # redis_client.save_orderbook(coin, data)
            time.sleep(rest_interval)

    def ws_thread():
        for coin in coin_list:
            print(f"[WS-{group_id}] {coin}: подписка через WebSocket")
            # Здесь будет запуск подписки
        while True:
            time.sleep(10)

    t1 = threading.Thread(target=rest_thread)
    t2 = threading.Thread(target=ws_thread)

    t1.start()
    t2.start()
    t1.join()
    t2.join()
