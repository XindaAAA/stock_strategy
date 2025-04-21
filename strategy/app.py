from transaction import Agent
from strategy_zoo.strategy_v1 import StrategyV1
from strategy_zoo.strategy_v2 import StrategyV2
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import os


class APP:
    """支持多策略选择的回测系统"""
    
    STRATEGY_MAP = {
        'v1': StrategyV1,
        'v2': StrategyV2
    }
    st = {70, 488, 525, 615, 669, 752, 793, 851, 889, 909, 989, 2005, 2024, 2092, 2124, 2168, 2197, 2200, 2251, 2259, 2289, 2316, 2388, 2424, 2425, 2485, 2490, 2528, 2569, 2592, 2602, 2650, 2656, 2721, 2742, 2748, 2808, 2822, 2872, 300029, 300052, 300096, 300097, 300125, 300137, 300147, 300163, 300165, 300175, 300205, 300300, 300313, 300343, 300368, 300376, 300419, 300555, 300600, 600136, 600190, 600287, 600303, 600358, 600360, 600365, 600381, 600568, 600599, 600603, 600608, 600671, 600711, 600777, 600831, 603007, 603377, 603388, 603557, 603828, 603869, 603879, 603959, 688287}

    def __init__(self, result_file_path, strategy_name='v1'):
        self.agent = Agent(result_file_path)
        self.set_strategy(strategy_name)

    def set_strategy(self, strategy_name):
        """设置当前使用的策略"""
        strategy_class = self.STRATEGY_MAP.get(strategy_name, StrategyV1)
        self.strategy = strategy_class()
        return self

    def show_pred_result(self, day, k=20, filt_st=True):
        """显示指定日期的预测结果"""
        print('{}预测结果'.format(day))
        result_list = []
        for code in self.agent.cur_position:
            i = self.agent.fetcher.get_rank_by_code(code, day)
            result_list.append([i, code, '（持仓）'])
        # topk股票
        for i in range(k):
            code = self.agent.fetcher.get_code_by_rank(i, day)
            if filt_st and code in self.st:
                continue
            if not code in self.agent.cur_position:
                result_list.append([i, code, ''])
        for i, code, tag in sorted(result_list, key=lambda item: item[0]):
            print('{:>4}. 股票代码 {:0>6} {}'.format(i, code, tag))

    def backtest(self, start_money=15_0000, strategy_name=None, filt_st=True):
        """回测"""
        os.makedirs('position', exist_ok=True)
        os.makedirs('result', exist_ok=True)
        if strategy_name is not None:
            self.set_strategy(strategy_name)
            
        money_left = start_money
        strategy = dict()
        total_money_list = []
        day_list = sorted(self.agent.fetcher.pred_result)
        # day_list = [day for day in day_list if day > '20250101']
        for day in day_list:
            # 交易，执行昨天策略
            for code in strategy:
                # 先卖出
                if strategy[code] < 0:
                    money_left = self.agent.transaction(code, day, strategy[code], money_left)
            for code in strategy:
                # 后买入
                if strategy[code] > 0:
                    money_left = self.agent.transaction(code, day, strategy[code], money_left)

            # 计算总权益
            total_money = money_left + self.agent.get_cur_capital(day)
            total_money_list.append(total_money)
            print(day, '总权益', total_money, '剩余金额', money_left)
            # 保存当前仓位信息
            with open(f'position/{day}.csv', 'w') as f:
                txt = '股票代码,当前仓位,开盘价,收盘价,市值,排名\n'
                for code in self.agent.cur_position:
                    amount = self.agent.cur_position[code]['amount']
                    open_ = self.agent.fetcher.get_open_by_code(code, day)
                    close = self.agent.fetcher.get_close_by_code(code, day)
                    rank = self.agent.fetcher.get_rank_by_code(code, day)
                    txt += f'{code},{amount},{round(open_, 2)},{round(close, 2)},{round(amount * open_)}, {rank}\n'
                f.write(txt)

            strategy = self.get_strategy(day, money_left, total_money, filt_st=filt_st)
        
        self.plot_total_money(day_list, total_money_list)

    def get_strategy(self, day, money_left, total_money, filt_st=True):
        stocks = dict()
        for code, stock_info in self.agent.cur_position.items():
            rank = self.agent.fetcher.get_rank_by_code(code, day)
            price = self.agent.fetcher.get_close_by_code(code, day)
            if price == 0 or rank == 9999:
                continue
            stocks[code] = {
                            'rank': rank,
                            'price': price,
                            'amount': stock_info['amount'],
                            'buy_price': stock_info['buy_price'],
                            }
        for rank in range(50):
            code = self.agent.fetcher.get_code_by_rank(rank, day)
            if filt_st and code in self.st:
                continue
            price = self.agent.fetcher.get_close_by_code(code, day)
            if price == 0:
                continue
            if code not in self.agent.cur_position:
                stocks[code] = {
                                'rank': rank, 
                                'price': price,
                                'amount': 0,
                                'buy_price': 0,
                                }
        return self.strategy.get_strategy(stocks, money_left, total_money)
        

    def plot_total_money(self, day_list, total_money_list):
        fig, ax = plt.subplots()
        ax.plot(day_list, total_money_list)
        # 设置刻度间隔，这里设置为每5天显示一个刻度
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))

        # 自动旋转x轴标签以防止重叠
        fig.autofmt_xdate()
        plt.savefig('result/fig.png')
        plt.show()


if __name__ == '__main__':
    app = APP('../data/result.csv')
    app.backtest(filt_st=True)
