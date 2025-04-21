import pandas as pd
import numpy as np
from datetime import datetime
import re

stock_data_path = '../../stock_data/data/stock_data.parquet'


def get_stock_data(start_time='2024-01-01', end_time=None):
    end_time = end_time or datetime.now().date().strftime('%Y-%m-%d')
    df = pd.read_parquet(stock_data_path)
    df['day'] = df['day'].astype(str)
    df.set_index(['code', 'day'], inplace=True)
    return df


def get_pred_result(result_file_path):
    pred_df = pd.read_csv(result_file_path)
    try:
        pred_df['time'] = pd.to_datetime(pred_df['time'], format='%Y%m%d').dt.date
    except ValueError:
        pred_df['time'] = pd.to_datetime(pred_df['time'], unit='s').dt.date
    pred_df['SecurityID'] = pred_df['SecurityID'].astype(int)
    result = dict()
    for day in pred_df['time'].unique():
        df = pred_df[pred_df['time'] == day].sort_values('pred', ascending=False)
        df = df.reset_index(drop=True)
        ordered_code = list(df['SecurityID'])
        # 过滤掉不能买的股票
        for code in ordered_code.copy():
            if '{:6>0}'.format(code).startswith('301'):
                ordered_code.remove(code)
        result[str(day).replace('-', '')] = ordered_code
    return result


class Fetcher:
    def __init__(self, result_file_path, today=None):
        if today is None:
            today = datetime.now().strftime("%Y-%m-%d")
        self.today = today
        self.data = get_stock_data(end_time=today)
        self.pred_result = get_pred_result(result_file_path)
    
    def get_close_by_code(self, code, day=None):
        """获取code今天的收盘价，出错返回0"""
        day = day or self.today
        day = day.replace('-', '')
        try:
            price = self.data.loc[(code, day)]['close'].item()
            if np.isnan(price):
                print(f'[WARNING] 股票{code}在{day}的收盘价为NaN')
                return 0
            else:
                return price
        except (KeyError, ValueError) as e:
            print(f'[WARNING] 获取股票{code}在{day}的收盘价失败: {str(e)}')
            return 0

    def get_open_by_code(self, code, day=None):
        """获取code今天的开盘价，出错返回0"""
        day = day or self.today
        day = day.replace('-', '')
        try:
            price = self.data.loc[(code, day)]['open'].item()
            if np.isnan(price):
                print(f'[WARNING] 股票{code}在{day}的开盘价为NaN')
                return 0
            else:
                return price
        except (KeyError, ValueError) as e:
            print(f'[WARNING] 获取股票{code}在{day}的开盘价失败: {str(e)}')
            return 0
        
    def get_rank_by_code(self, code, day=None):
        day = day or self.today
        day = day.replace('-', '')
        ordered_code = self.pred_result[day]
        if code in ordered_code:
            return ordered_code.index(code)
        else:
            print(f'[WARNING] 股票{code}不在{day}的预测结果中')
            return 9999
        
    def get_code_by_rank(self, rank, day=None):
        day = day or self.today
        day = day.replace('-', '')
        ordered_code = self.pred_result[day]
        return ordered_code[rank]
