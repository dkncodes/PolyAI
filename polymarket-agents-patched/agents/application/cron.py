import time

from scheduler import Scheduler as BaseScheduler
from scheduler.trigger import Monday

from agents.application.trade import Trader


class TradingScheduler:
    def __init__(self) -> None:
        self.trader = Trader()
        self.schedule = BaseScheduler()
        self.schedule.weekly(Monday(), self.trader.one_best_trade)

    def start(self) -> None:
        while True:
            self.schedule.exec_jobs()
            time.sleep(1)


if __name__ == "__main__":
    TradingScheduler().start()
