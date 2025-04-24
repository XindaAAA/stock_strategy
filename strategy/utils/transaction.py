from .fetcher import Fetcher
import os


class Agent:
    yongjin=0.0003
    guohufei=0.00001
    yinhuashui=0.0005

    def __init__(self, result_file_path, stock_data_path):
        self.fetcher = Fetcher(result_file_path, stock_data_path)
        self.cur_position = dict()
        self.cache = dict()

    def load_position(self, day, dirname='../data/position'):
        if '-' not in day:
            day = f'{day[:4]}-{day[4:6]}-{day[6:]}'
        with open(os.path.join(dirname, f'{day}.csv'), encoding='utf-8') as f:
            content = f.read().strip()
        cur_position = dict()
        for row in content.split('\n'):
            if not row:
                continue
            name, code, amount, _ = row.split(',')  # 忽略 buy_price 列
            cur_position[int(code)] = {'amount': int(amount)}
        self.set_position(cur_position)
        return cur_position

    def set_position(self, position):
        self.cur_position = position

    def get_cur_capital(self, day):
        capital = 0
        for code in self.cur_position:
            price = self.fetcher.get_close_by_code(code, day)
            if code not in self.cache and price != 0:
                self.cache[code] = price
            elif price == 0:  # 若当前交易日停牌，使用上一个有效收盘价
                price = self.cache[code]
            
            capital += self.cur_position[code]['amount'] * price
        return capital

    def transaction(self, code, day, amount, money):
        # 计算含税实际交易金额
        cost = self.cal_cost(code, day, amount)
        # 判断能否完成交易
        if amount > 0:  # 买入
            if money - cost < 0:  # 余额不足
                return money
        else:  # 卖出
            if code not in self.cur_position or self.cur_position[code]['amount'] + amount < 0:  # 剩余仓位不足
                return money
        # 执行交易
        if code not in self.cur_position:
            self.cur_position[code] = {'amount': 0, 'buy_price': 0}
        price = self.fetcher.get_open_by_code(code, day)
        if amount > 0:  # 买入时更新成本价
            total_amount = self.cur_position[code]['amount'] + amount
            total_cost = self.cur_position[code]['amount'] * self.cur_position[code]['buy_price'] + price * amount
            self.cur_position[code]['buy_price'] = total_cost / total_amount
        self.cur_position[code]['amount'] += amount
        if self.cur_position[code]['amount'] == 0:
            del self.cur_position[code]
        money -= cost
        return money
    
    def cal_cost(self, code, day, amount):
        price = self.fetcher.get_open_by_code(code, day)
        cost = price * abs(amount)
        # 计算佣金
        yongjin = cost * self.yongjin
        if yongjin < 5:  # 不免五
            yongjin = 5
        # 计算过户费
        guohufei = cost * self.guohufei
        if amount < 0:  # 卖出，收取印花税
            yinhuashui = cost * self.yinhuashui
            cost -= yongjin + guohufei + yinhuashui
            return -cost
        else:  # 买入
            cost += yongjin + guohufei
            return cost
