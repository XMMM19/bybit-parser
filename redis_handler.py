# redis_handler.py

import redis
import json
import datetime
from logger_config import setup_logger

logger = setup_logger("redis")

class RedisClient:
    def __init__(self, host="localhost", port=6379, db=0):
        self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    def save_orderbook(self, coin: str, data: dict):
        """
        Сохраняет стакан в формате, аналогичном старой версии парсера.  Для каждой
        монеты в Redis под ключом "<exchange>:<coin>" сохраняется JSON с
        полями: coin, exchange, asset_type, bids, asks, timestamp. Списки bids и
        asks сортируются по цене: bids — по убыванию, asks — по возрастанию.

        Параметр data ожидает словарь с ключами 'bids' и 'asks', где значения —
        последовательности из двух элементов [price, qty]. Если передаются
        дополнительные поля, они игнорируются.
        """
        # Определяем имя монеты. В старой реализации убирался суффикс USDT.
        coin_name = coin.replace('USDT', '')
        exchange = 'Bybit'
        asset_type = 'spot'
        # Получаем текущую метку времени в UTC
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Преобразуем заявки к списку кортежей и сортируем
        raw_bids = data.get('bids', []) or []
        raw_asks = data.get('asks', []) or []
        try:
            bids = sorted([(str(p), str(q)) for p, q in raw_bids], key=lambda x: float(x[0]), reverse=True)
        except Exception:
            bids = []
        try:
            asks = sorted([(str(p), str(q)) for p, q in raw_asks], key=lambda x: float(x[0]))
        except Exception:
            asks = []

        payload = {
            'coin': coin_name,
            'exchange': exchange,
            'asset_type': asset_type,
            'bids': bids,
            'asks': asks,
            'timestamp': now_iso
        }

        # Формируем ключ как "Биржа:Монета", например "Bybit:ADA"
        redis_key = f"{exchange}:{coin_name}"
        try:
            self.redis.set(redis_key, json.dumps(payload, ensure_ascii=False))
            logger.info(f"Сохранено: {redis_key}")
        except redis.RedisError as e:
            logger.error(f"[REDIS ERROR] {e}")

    def get_orderbook(self, coin: str) -> dict:
        """
        Возвращает сохранённый стакан для указанной монеты. Ключ формируется
        аналогично save_orderbook: "<exchange>:<coin>" с удалением суффикса USDT.
        Если ключ отсутствует или возникла ошибка, возвращается пустой словарь.
        """
        coin_name = coin.replace('USDT', '')
        redis_key = f"Bybit:{coin_name}"
        try:
            raw = self.redis.get(redis_key)
            return json.loads(raw) if raw else {}
        except redis.RedisError as e:
            logger.error(f"[REDIS ERROR] {e}")
            return {}

    def ping(self) -> bool:
        try:
            return self.redis.ping()
        except redis.RedisError:
            return False
