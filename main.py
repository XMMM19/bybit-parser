# main.py

import argparse
import sys
from config_loader import load_config
from process_supervisor import ProcessManager
from logger_config import setup_logger

logger = setup_logger("main")

def read_coins(file_path: str) -> list[str]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip().upper() for line in f if line.strip()]
    except FileNotFoundError:
        logger.warning(f"Файл не найден: {file_path}. Используем монеты по умолчанию.")
        return ["BTC", "ETH"]

def chunkify(lst: list, size: int) -> list[list]:
    return [lst[i:i + size] for i in range(0, len(lst), size)]

def main():
    parser = argparse.ArgumentParser(description="Bybit Orderbook Parser CLI")
    parser.add_argument("--config", type=str, default="config.yaml", help="Путь к конфигу")
    args = parser.parse_args()

    config = load_config(args.config)

    coins_file = config["coins_file"]
    coins_per_group = config["coins_per_process"]

    coin_list = read_coins(coins_file)
    coin_groups = chunkify(coin_list, coins_per_group)

    logger.info(f"Загружено {len(coin_list)} монет, запуск {len(coin_groups)} процессов")

    pm = ProcessManager(coin_groups, config)
    pm.start_all()
    pm.supervise()

if __name__ == "__main__":
    main()