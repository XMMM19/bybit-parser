# config_loader.py

import yaml
import os


class ConfigError(Exception):
    pass


def load_config(path: str = "config.yaml") -> dict:
    if not os.path.exists(path):
        raise ConfigError(f"Конфигурационный файл не найден: {path}")

    with open(path, "r", encoding="utf-8") as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigError(f"Ошибка разбора YAML: {e}")

    required_fields = ["coins_file", "coins_per_process", "redis", "proxy", "update", "features"]
    for field in required_fields:
        if field not in config:
            raise ConfigError(f"Отсутствует обязательный раздел: {field}")

    # Вложенные проверки
    for key in ["host", "port", "db"]:
        if key not in config["redis"]:
            raise ConfigError(f"Недостающий параметр redis.{key}")

    for key in ["rest_file", "ws_file"]:
        if key not in config["proxy"]:
            raise ConfigError(f"Недостающий параметр proxy.{key}")

    for key in ["rest_interval_sec", "max_ws_reconnect_attempts"]:
        if key not in config["update"]:
            raise ConfigError(f"Недостающий параметр update.{key}")
        
    for key in ["enable_rest", "enable_ws"]:
        if key not in config["features"]:
            raise ConfigError(f"Недостающий параметр features.{key}")

    return config
