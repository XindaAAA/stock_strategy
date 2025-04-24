from .base import StrategyBase
import math

class StrategyScreen(StrategyBase):
    """
    基于筛选法构建投资组合的策略
    
    策略原理：
    1. 对股票进行筛选，选择排名靠前的股票作为买入候选
    2. 买入策略：买入排名靠前的股票，不超过最大持仓数量
    3. 卖出策略：卖出排名靠后的持仓股票，不超过最大持仓数量

    策略参数：
    threshold_top: 买入前threshold_top只股票
    threshold_mid: 持有threshold_mid只股票

    回测结果：
    回测时间段: 20210104 至 20241216
    初始资金: 150000
    总收益率: 208.05%
    年化收益率: 32.95%
    最大回撤: 36.08%
    最大回撤发生时间段: 20240103 至 20240207
    修复时段: 20240207 至 20241031
    """

    def get_strategy(self, cur_position, day_result, day_data_window, money_left, principal):
        strategy = {}

        day_result = day_result.sort_values(by='pred', ascending=False)
        sorted_stocks = day_result.index.get_level_values(0).tolist()

        buy_list = sorted_stocks[:self.threshold_top]
        hold_list = sorted_stocks[self.threshold_top:self.threshold_top + self.threshold_mid]
        sell_list = sorted_stocks[self.threshold_top + self.threshold_mid:]

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