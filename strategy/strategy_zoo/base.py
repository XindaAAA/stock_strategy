import math

class StrategyBase:
    """定义策略基类，后续可以在这个基础上进行修改"""

    def __init__(self):
        ...

    def get_strategy(self, stocks, money_left=None, principal=None):
        """
        输入仓位数据及股票预测排名数据
        stocks: dict，键为股票代码，值为包含股票信息的字典，格式为{'rank': 预测收益率排名, 'price': 收盘价, 'amount': 当前仓位, 'buy_price': 成本价}

        输出策略
        strategy: dict，键为交易的股票代码，值为交易数量，值大于0代表买入，小于0代表卖出
        """
        ...
    