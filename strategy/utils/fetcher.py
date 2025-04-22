import pandas as pd
import numpy as np
from datetime import datetime


class Fetcher:
    def __init__(self, result_file_path):
        self.stock_data = self._get_stock_data()
        self.pred_result = self._get_pred_result(result_file_path)
        self.combined_data = self._merge_data()
        self.date_list = sorted(self.combined_data.index.get_level_values('day').unique())

    def _get_stock_data(self):
        df = pd.read_parquet('../../stock_data/data/stock_data.parquet')
        df['day'] = df['day'].astype(str)
        df.set_index(['code', 'day'], inplace=True)
        return df[['open', 'close']]

    def _get_pred_result(self, result_file_path):
        pred_df = pd.read_csv(result_file_path)
        try:
            pred_df['time'] = pd.to_datetime(pred_df['time'], format='%Y%m%d').dt.strftime('%Y%m%d')
        except ValueError:
            pred_df['time'] = pd.to_datetime(pred_df['time'], unit='s').dt.strftime('%Y%m%d')
        pred_df['SecurityID'] = pred_df['SecurityID'].astype(int)
        pred_df.set_index(['SecurityID', 'time'], inplace=True)
        return pred_df[['pred']]

    def _merge_data(self):
        # 重命名索引以匹配
        self.pred_result.index.names = ['code', 'day']
        merged_df = self.stock_data.join(self.pred_result[['pred']], how='inner')
        merged_df = merged_df[~merged_df.index.duplicated(keep='first')]
        return merged_df

    def get_data_by_date(self, date, window=1):
        """
        指定日期，获取自该日期开始往前 window 天的所有股票的数据

        :param date: 指定的日期，格式为 'YYYY-MM-DD'
        :param window: 往前追溯的天数，默认为 1
        :return: 包含指定日期范围内所有股票数据的 DataFrame
        """
        date = date.replace('-', '')
        end_index = self.date_list.index(date)
        start_index = max(0, end_index - window + 1)
        # 获取对应的交易日列表
        trading_days_range = self.date_list[start_index:end_index + 1]
        return self.combined_data[self.combined_data.index.get_level_values('day').isin(trading_days_range)]

    def get_close_by_code(self, code, day):
        """
        根据股票代码和日期获取对应股票的收盘价。若指定日期无数据，则返回该股票在距离指定日期最近的上一个交易日的收盘价。

        :param code: 股票代码
        :param day: 指定日期，格式为 'YYYYMMDD'
        :return: 对应股票在指定日期或最近上一个交易日的收盘价，如果都未找到则返回 None
        """
        try:
            return self.combined_data.loc[(code, day), 'close'].item()
        except KeyError:
            # 找到最近的上一个交易日
            trading_days = self.date_list
            index = trading_days.index(day) if day in trading_days else next((i for i, d in enumerate(trading_days) if d > day), 0)
            for prev_day in reversed(trading_days[:index]):
                try:
                    return self.combined_data.loc[(code, prev_day), 'close'].item()
                except KeyError:
                    continue
            return None

    def get_open_by_code(self, code, day):
        """
        根据股票代码和日期获取对应股票的开盘价。若指定日期无数据，则返回该股票在距离指定日期最近的上一个交易日的开盘价。

        :param code: 股票代码
        :param day: 指定日期，格式为 'YYYYMMDD'
        :return: 对应股票在指定日期或最近上一个交易日的开盘价，如果都未找到则返回 None
        """
        try:
            return self.combined_data.loc[(code, day), 'open'].item()
        except KeyError:
            # 找到最近的上一个交易日
            trading_days = self.date_list
            index = trading_days.index(day) if day in trading_days else next((i for i, d in enumerate(trading_days) if d > day), 0)
            for prev_day in reversed(trading_days[:index]):
                try:
                    return self.combined_data.loc[(code, prev_day), 'open'].item()
                except KeyError:
                    continue
            return None
