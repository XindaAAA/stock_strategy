from .base import StrategyBase
import math

class StrategyDemo(StrategyBase):
    """
    自定义策略实现

    策略原理:
    1. 按排名排序股票
    2. 卖出策略：卖出排名最靠后的持仓股票(排名>=min_sell_rank)
    3. 买入策略：买入排名靠前的股票(不超过最大持仓数量且总资金>=min_buy_value)

    策略参数:
    rebalance_freq: 调仓频率，即多少天调仓一次
    max_holding: 最大持仓数量
    sell_count: 每次调仓最大卖出股票数量
    min_buy_value: 最小买入金额
    min_sell_rank: 不卖出排名在此之前的股票

    回测结果:
    回测时间段: 20210104 至 20241216
    初始资金: 150000
    总收益率: 234.12%
    年化收益率: 35.71%
    最大回撤: 36.37%
    最大回撤发生时间段: 20240102 至 20240207
    修复时段: 20240207 至 20241008
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.counter = self.rebalance_freq - 1  # 调仓计数器

    def get_strategy(self, cur_position, day_result, day_data_window, money_left, principal):
        principal = principal or self.principal
        self.counter += 1
        if self.counter < self.rebalance_freq:
            return {}  # 未到调仓日
        
        self.counter = 0  # 重置计数器
        strategy = {}
        
        day_result = day_result.sort_values(by='pred', ascending=False)
        stocks = {}
        for (code, _), row in day_result.iterrows():
            stocks[code] = {
                'amount': cur_position.get(code, {'amount': 0})['amount'],
                'rank': len(stocks),
                'price': row['close']  # 假设使用收盘价作为价格
            }
        
        # 1. 按排名排序股票
        sorted_stocks = sorted(stocks.items(), key=lambda x: x[1]['rank'])
        # 2. 卖出策略：卖出排名最靠后的持仓股票(不超过实际持仓数量且排名>=min_sell_rank)
        holding_stocks = [s for s in sorted_stocks 
                         if s[1]['amount'] > 0 and s[1]['rank'] >= self.min_sell_rank]
        sell_num = min(self.sell_count, len(holding_stocks))
        if sell_num > 0:
            for code, _ in holding_stocks[-sell_num:]:
                sell_amount = stocks[code]['amount']
                strategy[code] = -sell_amount
                money_left += sell_amount * stocks[code]['price']

        # 3. 买入策略
        for code, stock in sorted_stocks:
            if money_left < principal / self.max_holding:
                break
            price = stock['price']
            if stock['amount'] == 0 and price > 0:
                
                max_amount = min(math.floor(money_left / price),
                                math.floor(principal / self.max_holding / price))
                max_amount = max_amount // 100 * 100  # 调整为100的倍数
                
                cost = max_amount * price
                if cost >= self.min_buy_value:
                    strategy[code] = max_amount
                    money_left -= cost
        return strategy
