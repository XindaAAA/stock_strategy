from .base import StrategyBase
import math

class StrategyV1(StrategyBase):
    """自定义策略实现"""
    
    def __init__(self):
        super().__init__()
        self.banned_codes = {}  # 禁用股票代码集合
        self.rebalance_freq = 1  # 调仓频率(每N天调仓一次)
        self.sell_count = 30  # 每次调仓最大卖出股票数量
        self.principal = 15_0000  # 本金
        self.max_buy_per_stock = 1 / 200  # 单只股票最大买入金额(元)
        self.min_buy_value = 1 / 400  # 最小买入金额(元)
        self.min_sell_rank = 400  # 不卖出排名在此之前的股票
        self.counter = self.rebalance_freq - 1  # 调仓计数器

    def is_banned(self, code):
        """检查股票是否在禁用列表中"""
        return code in self.banned_codes

    def get_strategy(self, cur_position, day_result, day_data_window, money_left=0, principal=15_0000):
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
            if money_left < self.max_buy_per_stock * principal:
                break
            price = stock['price']
            if (stock['amount'] == 0 and
                price > 0 and
                not self.is_banned(code)):
                
                max_amount = min(math.floor(money_left / price),
                                math.floor(self.max_buy_per_stock * principal / price))
                max_amount = max_amount // 100 * 100  # 调整为100的倍数
                
                cost = max_amount * price
                if cost >= self.min_buy_value * principal:
                    strategy[code] = max_amount
                    money_left -= cost
        return strategy
