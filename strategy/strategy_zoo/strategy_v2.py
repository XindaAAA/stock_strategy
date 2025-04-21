from .base import StrategyBase
import math

class StrategyV2(StrategyBase):
    """基于排名的稳健策略V2版本"""
    
    def __init__(self):
        super().__init__()
        # 策略参数
        self.max_position_ratio = 0.8  # 最大仓位比例
        self.min_trade_value = 5000    # 最小交易金额
        self.max_trade_value = 10000   # 最大交易金额
        self.top_rank = 20             # 只考虑前20名股票
        self.hold_limit = 5            # 最大持仓数量
        self.stop_loss_ratio = 0.95    # 止损比例
        self.take_profit_ratio = 1.15 # 止盈比例

    def get_strategy(self, stocks, money_left=None, principal=None):
        strategy = {}
        if money_left is None or principal is None:
            return strategy
            
        # 1. 计算当前仓位价值
        position_value = sum(
            s['amount'] * s['price'] 
            for s in stocks.values() 
            if s['amount'] > 0
        )
        total_assets = money_left + position_value
        max_position = total_assets * self.max_position_ratio
        
        # 2. 卖出策略
        for code, stock in stocks.items():
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
                
                # 卖出排名靠后的持仓股
                elif stock['rank'] > self.top_rank:
                    strategy[code] = -stock['amount']
                    money_left += stock['amount'] * current_price
        
        # 3. 买入策略
        available_cash = min(money_left, max_position - position_value)
        
        # 获取前top_rank名股票
        top_stocks = [
            (code, stock) 
            for code, stock in stocks.items() 
            if stock['amount'] == 0 and stock['rank'] <= self.top_rank
        ]
        # 按排名从高到低排序
        top_stocks.sort(key=lambda x: x[1]['rank'])
        
        # 控制持仓数量
        current_holdings = len([s for s in stocks.values() if s['amount'] > 0])
        max_new_positions = max(0, self.hold_limit - current_holdings)
        
        for code, stock in top_stocks[:max_new_positions]:
            if available_cash < self.min_trade_value:
                break
                
            price = stock['price']
            if price <= 0:
                continue
                
            # 计算交易数量
            trade_value = min(self.max_trade_value, available_cash)
            amount = math.floor(trade_value / price)
            amount = max(amount // 100 * 100, 100)  # 整手交易
            
            if amount * price >= self.min_trade_value:
                strategy[code] = amount
                available_cash -= amount * price
        
        return strategy