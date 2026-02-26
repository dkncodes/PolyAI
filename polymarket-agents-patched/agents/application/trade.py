from agents.application.executor import Executor as Agent
from agents.polymarket.gamma import GammaMarketClient as Gamma
from agents.polymarket.polymarket import Polymarket

import shutil
import time


class Trader:
    def __init__(self):
        self.polymarket = Polymarket()
        self.gamma = Gamma()
        self.agent = Agent()

    def pre_trade_logic(self) -> None:
        self.clear_local_dbs()

    def clear_local_dbs(self) -> None:
        for path in ["local_db_events", "local_db_markets"]:
            try:
                shutil.rmtree(path)
            except FileNotFoundError:
                pass
            except Exception as err:
                print(f"[warn] could not delete {path}: {err}")

    def one_best_trade(self, max_retries: int = 3, retry_sleep_seconds: int = 3) -> None:
        """
        one_best_trade evaluates events, markets, and orderbooks,
        then computes a trade candidate.

        Safety: bounded retries to avoid infinite recursion/runaway loops.
        """
        last_error = None

        for attempt in range(1, max_retries + 1):
            try:
                self.pre_trade_logic()

                events = self.polymarket.get_all_tradeable_events()
                print(f"1. FOUND {len(events)} EVENTS")

                filtered_events = self.agent.filter_events_with_rag(events)
                print(f"2. FILTERED {len(filtered_events)} EVENTS")

                markets = self.agent.map_filtered_events_to_markets(filtered_events)
                print()
                print(f"3. FOUND {len(markets)} MARKETS")

                print()
                filtered_markets = self.agent.filter_markets(markets)
                print(f"4. FILTERED {len(filtered_markets)} MARKETS")

                if not filtered_markets:
                    print("[info] No markets passed filters. Skipping trade.")
                    return

                market = filtered_markets[0]
                best_trade = self.agent.source_best_trade(market)
                print(f"5. CALCULATED TRADE {best_trade}")

                amount = self.agent.format_trade_prompt_for_execution(best_trade)
                print(f"6. SAFE-SIZED AMOUNT {amount}")

                # Please refer to TOS before uncommenting: polymarket.com/tos
                # trade = self.polymarket.execute_market_order(market, amount)
                # print(f"7. TRADED {trade}")
                return

            except Exception as e:
                last_error = e
                print(f"[error] attempt {attempt}/{max_retries} failed: {e}")
                if attempt < max_retries:
                    time.sleep(retry_sleep_seconds)

        raise RuntimeError(f"one_best_trade failed after {max_retries} retries: {last_error}")

    def maintain_positions(self):
        pass

    def incentive_farm(self):
        pass


if __name__ == "__main__":
    t = Trader()
    t.one_best_trade()
