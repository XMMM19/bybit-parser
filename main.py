# main.py

import argparse
from multiprocessing import Process
from config_loader import load_config
from pathlib import Path
import sys
import time

from process_manager import run_group_worker  # пока только объявим

def read_coins(file_path: str) -> list[str]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip().upper() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[ПРЕДУПРЕЖДЕНИЕ] Файл не найден: {file_path}. Используем монеты по умолчанию.", file=sys.stderr)
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

    print(f"[INFO] Загружено {len(coin_list)} монет, запуск {len(coin_groups)} процессов")

    processes = []

    for idx, group in enumerate(coin_groups):
        p = Process(target=run_group_worker, args=(idx, group, config))
        p.start()
        processes.append(p)

    # Ожидаем завершения всех дочерних процессов
    for p in processes:
        p.join()


if __name__ == "__main__":
    main()
