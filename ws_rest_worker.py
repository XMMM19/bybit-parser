# ws_rest_worker.py

import json
import websocket
import time
import threading
import requests
import re
import sys
import socks
import certifi
import ssl
from logger_config import setup_logger

logger = setup_logger("ws_group")

def parse_proxy(proxy: str, proxy_type: str = "http"):
    match = re.match(r"([^:]+):([^@]+)@([\d.]+):(\d+)", proxy)
    if not match:
        return None
    user, pwd, host, port = match.groups()
    return host, int(port), (user, pwd), proxy_type

def start_rest_worker(group_id: int, coin_list: list[str], redis_client, rest_proxy: str, interval: int):
    def rest_loop():
        while True:
            for coin in coin_list:
                try:
                    url = f"https://api.bybit.com/v5/market/orderbook?category=spot&symbol={coin}"
                    proxies = {"http": rest_proxy, "https": rest_proxy} if rest_proxy else None
                    response = requests.get(url, proxies=proxies, timeout=10)

                    if response.status_code == 200:
                        data = response.json()
                        redis_client.save_orderbook(coin, {
                            "bids": data.get("result", {}).get("bids", []),
                            "asks": data.get("result", {}).get("asks", []),
                            "source": "REST"
                        })
                        logger.info(f"[REST-{group_id}] Обновлено: {coin}")
                    else:
                        logger.warning(f"[REST-{group_id}] Ошибка ответа {coin}: {response.status_code}")
                except Exception as e:
                    logger.error(f"[REST-{group_id}] Ошибка запроса {coin}: {e}")
            time.sleep(interval)

    t = threading.Thread(target=rest_loop, daemon=True)
    t.start()
    return t

def start_ws_worker(group_id: int, coin_list: list[str], redis_client, ws_proxy: str, max_attempts: int):
    def on_message(ws, message):
        try:
            data = json.loads(message)
            if data.get("topic", "").startswith("orderbook.40."):
                symbol = data["topic"].split(".")[-1]
                orderbook = {
                    "bids": data.get("data", {}).get("b", []),
                    "asks": data.get("data", {}).get("a", []),
                    "source": "WS"
                }
                redis_client.save_orderbook(symbol, orderbook)
        except Exception as e:
            logger.error(f"[WS-{group_id}] Ошибка обработки сообщения: {e}")

    def on_error(ws, error):
        logger.error(f"[WS-{group_id}] Ошибка WebSocket: {error}")

    def on_close(ws, close_status_code, close_msg):
        logger.warning(f"[WS-{group_id}] Соединение закрыто: {close_status_code} / {close_msg}")

    def on_open(ws):
        logger.info(f"[WS-{group_id}] WebSocket открыт, подписка на монеты")
        for symbol in coin_list:
            payload = {
                "op": "subscribe",
                "args": [f"orderbook.{depth}.{symbol}"]
            }
            ws.send(json.dumps(payload))

    def run_ws():
        reconnect_attempts = 0
        while reconnect_attempts < max_attempts:
            try:
                ws_url = "wss://stream.bybit.com/v5/public/spot"
                ws_opts = {
                    "on_open": on_open,
                    "on_message": on_message,
                    "on_error": on_error,
                    "on_close": on_close
                }

                ws_app = websocket.WebSocketApp(ws_url, **ws_opts)

                # Используем certifi для проверки SSL-сертификатов: задаём ca_certs и cert_reqs.
                ssl_opts = {"ca_certs": certifi.where(), "cert_reqs": ssl.CERT_REQUIRED}

                if ws_proxy:
                    parsed = parse_proxy(ws_proxy, proxy_type="socks5")
                    if parsed:
                        host, port, auth, proxy_type = parsed
                        logger.debug(f"[WS-{group_id}] Подключение через SOCKS5 {host}:{port}")
                        ws_app.run_forever(
                            http_proxy_host=host,
                            http_proxy_port=port,
                            http_proxy_auth=auth,
                            proxy_type=proxy_type,
                            sslopt=ssl_opts,
                        )
                    else:
                        logger.warning(f"[WS-{group_id}] Некорректный формат прокси: {ws_proxy}")
                        ws_app.run_forever(sslopt=ssl_opts)
                else:
                    ws_app.run_forever(sslopt=ssl_opts)

            except Exception as e:
                logger.error(f"[WS-{group_id}] Ошибка соединения: {e}")
                reconnect_attempts += 1
                time.sleep(5)

        logger.error(f"[WS-{group_id}] Превышено число попыток подключения, завершение")

    t = threading.Thread(target=run_ws, daemon=True)
    t.start()
    return t