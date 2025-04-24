# stock_strategy

## 准备工作
- 在[stock_data](https://github.com/leempire/stock_data)项目中完成配置后，使用`python tools/download_data.py --mode 4`导出文件到`./data/stock_data.parquet`
- 获取模型预测信号，保存在`./data/result.csv`

## 回测策略文档
- 在`./strategy/strategy_zoo`中参考`demo.py`的格式新建策略
- 在`./strategy/app.py`中导入新建的策略，添加到`APP.STRATEGY_MAP`中
- 使用`python run_backtest.py --strategy demo`运行回测

注：
- 若某只持仓股在某个交易日停牌，在计算当天资产时，该股票市值上一个有效交易日的收盘价计算

## 更新日志
#### v1.0
- 更新了Strategy的输入，详情参考`./strategy/strategy_zoo/base.py`和`./strategy/strategy_zoo/strategy_demo.py`
- 更新了代码规范，新提交的策略需注明策略原理、策略参数、回测结果信息，参考`./strategy/strategy_zoo/strategy_demo.py`，注意统一初始资金和回测时段
- 策略中的超参数定义参考`./strategy/run_backtest.py`，新增的参数在代码中注明相应策略名称
