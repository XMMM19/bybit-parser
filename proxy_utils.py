# proxy_utils.py

import random
import os
from logger_config import setup_logger

logger = setup_logger("proxy")

def load_proxies(proxy_file: str) -> list[str]:
    if not os.path.exists(proxy_file):
        logger.warning(f"Файл прокси не найден: {proxy_file}")
        return []

    with open(proxy_file, "r", encoding="utf-8") as f:
        proxies = [line.strip() for line in f if line.strip()]
        logger.info(f"Загружено {len(proxies)} прокси из {proxy_file}")
        return proxies

def get_random_proxy(proxy_file: str) -> str | None:
    proxies = load_proxies(proxy_file)
    if not proxies:
        return None
    return random.choice(proxies)
