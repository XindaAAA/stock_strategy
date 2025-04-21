# stock_strategy

## 准备工作
- 将`./strategy/fetcher.py`中的`stock_data_path`指向[stock_data](https://github.com/leempire/stock_data)项目中`python tools/download_data.py --mode 4`导出的文件

## 回测策略文档
- 在`./strategy/strategy_zoo`中参考`strategy_v1.py`的格式新建策略
- 在`./strategy/app.py`中导入新建的策略，并在`APP`类的初始化方法中选择新建的策略
- 运行`python app.py`即可进行回测，回测结果保存在`./strategy/result`目录下

注：
- 若某只持仓股在某个交易日停牌，在计算当天资产时，该股票市值上一个有效交易日的收盘价计算
