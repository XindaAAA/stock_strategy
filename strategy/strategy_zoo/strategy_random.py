from .base import StrategyBase
import random

class StrategyRandom(StrategyBase):
    """
    随机买卖策略

    策略原理:
    1. 随机卖出一定数量的股票
    2. 随机买入一定数量的股票

    策略参数:
    sell_count: 每次调仓卖出股票数量
    min_buy_value: 最小买入金额
    max_holding: 最大持仓数量

    回测结果:
    回测时间段: 20210104 至 20241216
    初始资金: 150000
    总收益率: -22.82%
    年化收益率: -6.35%
    最大回撤: 55.68%
    最大回撤发生时间段: 20220303 至 20240918
    修复时段: 20240918 至 未修复
    """

    def get_strategy(self, cur_position, day_result, day_data_window, money_left, principal):
        strategy = {}
        # 随机卖出4支
        holding_codes = list(cur_position.keys())
        random.shuffle(holding_codes)
        for code in holding_codes[:self.sell_count]:
            amount = cur_position[code]['amount']
            try:
                price = day_result.loc[(code, ), 'close'].item()
            except Exception:
                continue
            strategy[code] = -amount
            money_left += amount * price
        # 随机买入15支股票
        codes = day_result.index.get_level_values(0).tolist()
        random.shuffle(codes)
        while money_left > self.min_buy_value:
            code = codes.pop()
            price = day_result.loc[(code, ), 'close'].item()
            amount = principal / self.max_holding / price
            amount = max(amount // 100 * 100, 100)  # 整手交易
            strategy[code] = amount
            money_left -= amount * price
        return strategy
