# stock_strategy

## 准备工作
- 将`./strategy/fetcher.py`中的`stock_data_path`指向[stock_data](https://github.com/leempire/stock_data)项目中`python tools/download_data.py --mode 4`导出的文件

## 回测策略文档
- 在`./strategy/strategy_zoo`中参考`strategy_v2.py`的格式新建策略
- 在`./strategy/app.py`中导入新建的策略，并在`APP`类的初始化方法中选择新建的策略
- 运行`python app.py`即可进行回测，回测结果保存在`./strategy/result`目录下，每天的仓位保存在`./strategy/position`目录下

注：
- 若某只持仓股在某个交易日停牌，在计算当天资产时，该股票市值按0计算
- 回测时filt_st参数决定是否过滤st股票，若置为True，需更改以下文件：
  - 在`./strategy/transaction.py`中使用fetcher_stock_data.py中的Fetcher
  - 修改`./strategy/stock_database_api/mysql_manager.py`中修改数据库相应配置，以获取股票名称
