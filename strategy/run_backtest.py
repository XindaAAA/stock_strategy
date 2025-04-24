from app import APP
import argparse
import random
import numpy as np


parser = argparse.ArgumentParser(description='执行回测')
parser.add_argument('--strategy', type=str, default='demo', help='策略名称')
parser.add_argument('--start_money', type=int, default=15_0000, help='初始资金')
parser.add_argument('--result_file_path', type=str, default='../data/result.csv', help='结果文件路径')
parser.add_argument('--stock_data_path', type=str, default='../data/stock_data.parquet', help='股票数据文件路径')
parser.add_argument('--seed', type=int, default=1, help='随机种子，0为不设置种子')
parser.add_argument('--window', type=int, default=20, help='窗口大小，用于计算策略，默认为20天')
# 策略参数
# demo
parser.add_argument('--rebalance_freq', type=int, default=1, help='每多少天重新平衡仓位')
parser.add_argument('--max_holding', type=int, default=15, help='最大持仓数量')
parser.add_argument('--sell_count', type=int, default=4, help='每次调仓最大卖出股票数量')
parser.add_argument('--min_buy_value', type=int, default=3000, help='最小买入金额')
parser.add_argument('--min_sell_rank', type=int, default=200, help='不卖出排名在此之前的股票')
# screen
parser.add_argument('--threshold_top', type=int, default=10, help='买入前threshold_top只股票')
parser.add_argument('--threshold_mid', type=int, default=200, help='持有threshold_mid只股票')
# stop
parser.add_argument('--stop_loss_ratio', type=float, default=0.85, help='止损率')
parser.add_argument('--take_profit_ratio', type=float, default=1.30, help='止盈率')

args = parser.parse_args()
# 设置随机种子
if args.seed != 0:
    random.seed(args.seed)
    np.random.seed(args.seed)

app = APP(result_file_path=args.result_file_path, stock_data_path=args.stock_data_path)
app.set_strategy(
    strategy_name=args.strategy,
    # 策略参数
    # demo
    rebalance_freq=args.rebalance_freq,
    max_holding=args.max_holding,
    sell_count=args.sell_count,
    min_buy_value=args.min_buy_value,
    min_sell_rank=args.min_sell_rank,
    # screen
    threshold_top=args.threshold_top,
    threshold_mid=args.threshold_mid,
    #stop
    stop_loss_ratio = args.stop_loss_ratio,
    take_profit_ratio = args.take_profit_ratio,
)
app.backtest(start_money=args.start_money, window=args.window)
