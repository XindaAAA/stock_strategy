from .base import StrategyBase
import math

class StrategyVX1(StrategyBase):
    """自定义策略实现"""
    
    def __init__(self):
        super().__init__()
        self.banned_codes = {600168, 40, 600289, 600811, 600070, 600811, 2200, 600157}  # 禁用股票代码集合
        self.rebalance_freq = 1  # 调仓频率(每N天调仓一次)
        self.sell_count = 2  # 每次调仓最大卖出股票数量
        self.principal = 15_0000  # 本金
        self.max_buy_per_stock = 1 / 15  # 单只股票最大买入金额(元)
        self.min_buy_value = 1 / 30  # 最小买入金额(元)
        self.min_sell_rank = 80  # 不卖出排名在此之前的股票
        self.counter = self.rebalance_freq - 1  # 调仓计数器
        self.stop_loss_ratio = 0.85    # 止损比例
        self.take_profit_ratio = 1.30 # 止盈比例

    def is_banned(self, code):
        """检查股票是否在禁用列表中"""
        return code in self.banned_codes

    def get_strategy(self, stocks, money_left=None, principal=None):
        principal = principal or self.principal
        self.counter += 1
        if self.counter < self.rebalance_freq:
            return {}  # 未到调仓日
        
        self.counter = 0  # 重置计数器
        strategy = {}
        # 1. 按排名排序股票
        sorted_stocks = sorted(stocks.items(), key=lambda x: x[1]['rank'])
        
        # 2.a 卖出策略1：止损检查与止盈检查
        for code, stock in sorted_stocks:
            if stock['amount'] > 0:
                current_price = stock['price']
                cost_price = stock['buy_price']
                
                # 止损检查
                if current_price <= cost_price * self.stop_loss_ratio:
                    strategy[code] = -stock['amount']
                    money_left += stock['amount'] * current_price
                
                # 止盈检查
                elif current_price >= cost_price * self.take_profit_ratio:
                    strategy[code] = -stock['amount']
                    money_left += stock['amount'] * current_price
                        
        # 2.b  卖出策略2：卖出排名最靠后的持仓股票(不超过实际持仓数量且排名>=min_sell_rank)，且不操作已经止损止盈过的
        holding_stocks = [s for s in sorted_stocks 
                         if s[1]['amount'] > 0 and s[1]['rank'] >= self.min_sell_rank and strategy.get(s[0]) is None ]
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
