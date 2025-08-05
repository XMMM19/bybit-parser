# Парсер стаканов Bybit
Проект собирает стаканы (orderbook) спотовых инструментов биржи Bybit по REST и WebSocket и сохраняет их в Redis. Список монет считывается из файла, делится на группы и обрабатывается в отдельных процессах.

## Требования
- Python 3.10+  
- Зависимости из `requirements.txt`  
- Рабочий экземпляр Redis, доступный по параметрам в конфигурации

## Установка
```bash
git clone <адрес-репозитория>
cd bybit-parser
python -m venv venv
source venv/bin/activate        # или venv\Scripts\activate в Windows
pip install -r requirements.txt
```

## Конфигурация
Приложение использует YAML‑файл конфигурации (по умолчанию config.yaml), в котором должны присутствовать обязательные секции: coins_file, coins_per_process, redis, proxy, update и logging. Пример:
```yaml
coins_file: "test_120.txt"
coins_per_process: 10

redis:
  host: "localhost"
  port: 6379
  db: 0

proxy:
  rest_file: "proxies_bybit_h.txt"
  ws_file: "proxies_bybit_s.txt"

update:
  rest_interval_sec: 60
  max_ws_reconnect_attempts: 3
  orderbook_depth: 1

logging:
  level: "INFO"
  to_file: true
  log_dir: "logs"
```

## Файлы монет
Файл монет (coins_file) — по одной тикерной паре без суффикса USDT в строке (например, BTC, ETH).

## Запуск
Входная точка проекта — main.py. Запустите:
```bash
python main.py --config path/to/config.yaml
```
Параметр --config опционален; без него используется config.yaml в корне проекта.

## Как это работает
1. Список монет делится на группы по coins_per_process. Для каждой группы создаётся отдельный процесс.
2. В каждом процессе запускаются два потока:
   - REST‑поток периодически запрашивает книгу ордеров и сохраняет её в Redis.
   - WebSocket‑поток подписывается на обновления стакана и также пишет их в Redis.
3. Данные сохраняются в формате Bybit:<монета> с полями bids, asks, timestamp и т.д.

## Логирование
Логи выводятся в консоль и в директорию logs (если включено в конфигурации). Каждый модуль ведёт собственный лог.
