from .base import StrategyBase
import random

class StrategyRandom(StrategyBase):
    """自定义策略实现"""

    def get_strategy(self, cur_position, day_result, day_data_window, money_left=0, principal=15_0000):
        strategy = {}
        # 随机卖出30支
        holding_codes = list(cur_position.keys())
        random.shuffle(holding_codes)
        for code in holding_codes[:30]:
            amount = cur_position[code]['amount']
            try:
                price = day_result.loc[(code, ), 'close'].item()
            except Exception:
                continue
            strategy[code] = -amount
            money_left += amount * price
        # 随机买入200支股票
        codes = day_result.index.get_level_values(0).tolist()
        random.shuffle(codes)
        while money_left > 1_0000:
            code = codes.pop()
            price = day_result.loc[(code, ), 'close'].item()
            amount = principal / 200 / price
            amount = max(amount // 100 * 100, 100)  # 整手交易
            strategy[code] = amount
            money_left -= amount * price
        return strategy
