# redis_handler.py

import redis
import json


class RedisClient:
    def __init__(self, host="localhost", port=6379, db=0):
        self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    def save_orderbook(self, coin: str, data: dict):
        key = f"orderbook:{coin}"
        try:
            self.redis.set(key, json.dumps(data))
            print(f"[REDIS] Сохранено: {key}")
        except redis.RedisError as e:
            print(f"[REDIS ERROR] {e}")

    def get_orderbook(self, coin: str) -> dict:
        key = f"orderbook:{coin}"
        try:
            raw = self.redis.get(key)
            return json.loads(raw) if raw else {}
        except redis.RedisError as e:
            print(f"[REDIS ERROR] {e}")
            return {}

    def ping(self) -> bool:
        try:
            return self.redis.ping()
        except redis.RedisError:
            return False
