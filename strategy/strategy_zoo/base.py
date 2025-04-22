import math

class StrategyBase:
    """定义策略基类，后续可以在这个基础上进行修改"""

    def __init__(self):
        ...

    def get_strategy(self, cur_position, day_result, day_data_window, money_left=0, principal=15_0000):
        """
        输入仓位数据及股票预测排名数据
        cur_position: dict，当前仓位，键为股票代码，值为dict，包含amount
        day_result: DataFrame，当天所有股票数据，索引为(code, day)，列为open, close, pred，pred代表预测收益率
        day_data_window: DataFrame，过去若干天的所有股票数据，索引为(code, day)，列为open, close, pred，pred代表预测收益率，包含最近20天的数据
        money_left: 剩余资金
        principal: 总权益

        输出策略
        strategy: dict，键为交易的股票代码，值为交易数量，值大于0代表买入，小于0代表卖出
        """
        ...
    