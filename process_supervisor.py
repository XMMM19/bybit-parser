# process_supervisor.py

from multiprocessing import Process
import time
from process_manager import run_group_worker
import logging
# from logger_config import setup_logger

# logger = setup_logger("supervisor")

logger = logging.getLogger("supervisor")

class ProcessManager:
    def __init__(self, coin_groups: list[list[str]], config: dict):
        self.coin_groups = coin_groups
        self.config = config
        self.processes: dict[int, Process] = {}

    def start_all(self):
        for idx, group in enumerate(self.coin_groups):
            self._start_process(idx, group)

    def _start_process(self, group_id: int, coin_group: list[str]):
        logger.info(f"Запуск процесса группы {group_id}")
        p = Process(target=run_group_worker, args=(group_id, coin_group, self.config))
        p.start()
        self.processes[group_id] = p

    def supervise(self):
        try:
            while True:
                for group_id, process in list(self.processes.items()):
                    if not process.is_alive():
                        logger.warning(f"Процесс {group_id} упал. Перезапуск...")
                        self._start_process(group_id, self.coin_groups[group_id])
                time.sleep(10)
        except KeyboardInterrupt:
            logger.info("Завершение по Ctrl+C")
            for p in self.processes.values():
                p.terminate()