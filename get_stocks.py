
from rqalpha.api import *
from logbook import TimedRotatingFileHandler
from rqalpha.utils.logger import user_log as log
from rqalpha.utils.logger import user_std_handler_log_formatter, user_system_log
import string
import talib
import sys 
import os
sys.path.append("/home/wl/oneb/") 
from macd import *

user_file_handler = TimedRotatingFileHandler("/home/wl/log.txt")
user_file_handler.formatter = user_std_handler_log_formatter
log.handlers.append(user_file_handler)
user_system_log.handlers.append(user_file_handler)

def trim_order(orders):
    neworders = []
    for order in orders:
        if instruments(order).days_from_listed() > 130:
            neworders.append(order)
    return neworders


def init(context):
    context.stocks = []
    context.stocks.extend(sector("Financials"))
    
    context.stocks.extend(sector("Energy"))
    context.stocks.extend(sector("Materials"))
    context.stocks.extend(sector("ConsumerDiscretionary"))
    context.stocks.extend(sector("ConsumerStaples"))
    context.stocks.extend(sector("HealthCare"))
    context.stocks.extend(sector("Financials"))
    context.stocks.extend(sector("InformationTechnology"))
    context.stocks.extend(sector("TelecommunicationServices"))
    context.stocks.extend(sector("Utilities"))
    context.stocks.extend(sector("Industrials"))

    print(context.stocks)
    context.stocks = trim_order(context.stocks)
    print(context.stocks)

    context.SHORTPERIOD = 20
    context.LONGPERIOD = 120

    context.planorder = 0

def before_trading_init(context):
    context.sellout = 0 # 1 means sell out all of the stock
    context.planorder = 0
    curslope = 0
    context.prices = {}
    context.short_avg = {}
    context.long_avg = {}
    context.volume = {}
    context.total_turnover = {}


    for order in context.stocks:
        context.prices[order] = history_bars(order, context.LONGPERIOD+1, '1d', 'close')
        context.volume[order] = history_bars(order, context.LONGPERIOD+1, '1d', 'volume')

	
	
def before_trading(context):
    before_trading_init(context)
    macd_trim(context)
    
    macd_judge(context)

def handle_bar(context, bar_dict):
    # bar_dict[order_book_id]
    # context.portfolio 

    if context.sellout:
        for order in getcurrentorder(context):
            log.info("sellout: " + order)
            order_target_value(order, 0)
        plot("sellout", 1)
    else:
        plot("sellout", 0)

    for exe in context.exe:
        if exe[1] == 'buy':
            order = exe[0]
            shares = context.portfolio.cash / bar_dict[order].close
            log.info("cash: " + str(context.portfolio.cash) + " buy: " + order + " shares:" + str(shares))
            order_shares(order, shares)
    if context.portfolio.units == 0:
        log.info("empty")
        plot("empty", 2)
