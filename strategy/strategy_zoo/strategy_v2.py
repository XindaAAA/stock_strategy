from .base import StrategyBase
import math

class StrategyV2(StrategyBase):
    """基于筛选法构建投资组合的策略"""
    
    def __init__(self):
        super().__init__()
        # 筛选参数
        self.top_buy_count = 80  # 买入前top_buy_count只股票
        self.middle_hold_count = 420  # 持有middle_hold_count只股票
        self.target_portfolio_size = 50

    def get_strategy(self, cur_position, day_result, day_data_window, money_left=0, principal=15_0000):
        strategy = {}

        day_result = day_result.sort_values(by='pred', ascending=False)
        sorted_stocks = day_result.index.get_level_values(0).tolist()

        buy_list = sorted_stocks[:self.top_buy_count]
        hold_list = sorted_stocks[self.top_buy_count:self.top_buy_count + self.middle_hold_count]
        sell_list = sorted_stocks[self.top_buy_count + self.middle_hold_count:]

        current_holdings = list(cur_position.keys())

        # 卖出策略
        for code in current_holdings:
            if code in sell_list:
                strategy[code] = -cur_position[code]['amount']
                money_left += cur_position[code]['amount'] * day_result.loc[(code, ), 'close'].item()

        # 买入策略
        available_cash = money_left
        buy_candidates = [code for code in buy_list if code not in current_holdings]
        for code in buy_candidates:
            if available_cash <= 0:
                break
            price = day_result.loc[(code, ), 'close'].item()
            if price > 0:
                # 等权重买入
                amount = math.floor(available_cash / len(buy_candidates) / price)
                amount = max(amount // 100 * 100, 100)  # 整手交易
                if amount * price > 0:
                    strategy[code] = amount
                    available_cash -= amount * price

        return strategy