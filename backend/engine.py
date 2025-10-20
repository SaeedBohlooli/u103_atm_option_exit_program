import ib_insync.util as ib_util
import pprint
from pandas import ExcelWriter
from ib_insync import *
import time
import logging.handlers
import numpy as np
from tabulate import tabulate
import os
import logging
import pandas as pd
import configparser
#import yaml
import argparse
import datetime
from collections import defaultdict
import sys
from ruamel.yaml import YAML
import json


yaml = YAML()
yaml.preserve_quotes = True  # Optional: preserve quotes if any

sys.path.insert(0, f'../')
for dir_1 in os.listdir(os.path.join('../')):
    if (dir_1.startswith("a") or dir_1.startswith("u") ):
        sys.path.insert(0, f'../{dir_1}')

from utils import miscutils

parser = argparse.ArgumentParser()
parser.add_argument('--portfolio-id', help="active portfolio", default='000')
args = parser.parse_args()
portfolio_id = args.portfolio_id
if portfolio_id == '000':
    print('you need to pass portfoli like  --p-id=p100')
    exit()

intermediate_dir = f'../../portfolios/intermediate/{portfolio_id}'
flatten_fill_file_path = f'{intermediate_dir}/86-ib-flatten_fill_df.csv'

configs_folder = f'../configs'
portfolio_dir = f'../../portfolios/results/{portfolio_id}'
reports_dir = f'../../portfolios/reports/{portfolio_id}'
intermediate_dir = f'../../portfolios/intermediate/{portfolio_id}'
log_dir = f'../../portfolios/logs/{portfolio_id}'
detailed_log_dir = f'../../portfolios/detailed-logs/{portfolio_id}'
shared_dir = f'../shared'

os.makedirs(portfolio_dir, exist_ok=True)
os.makedirs(reports_dir, exist_ok=True)
os.makedirs(intermediate_dir, exist_ok=True)
os.makedirs(detailed_log_dir, exist_ok=True)
os.makedirs(log_dir, exist_ok=True)


application_state_file_path = f'{intermediate_dir}/84-application_state.csv'
user_input_file_path = f'{shared_dir}/params.json'
executed_orders_from_ib_ver_2_file_path = f'{intermediate_dir}/90-executed_orders_from_ib_ver_2.csv'

def load_config(path = 'config.yaml') -> dict:
    with open(path, 'r') as file:
#        config = yaml.safe_load(file)
        # TODO, we used this one as we watn to update the yaml as is ...
        config = yaml.load(file)
    return config

def load_app_config():
    global app_config
    conf_file = f'{configs_folder}/config-{portfolio_id}.yaml'
    print(f'loading config file ....conf_file: {conf_file}')
    config = load_config(conf_file)
    app_config = config
    return app_config

def reload_app_config():
    global app_config
    logger.info('loading config file ....')
    config = load_config(f'{configs_folder}/config-{portfolio_id}.yaml')#['default']
    logger.info('loading config file is done ....')
    app_config = config
    return app_config

app_config = load_app_config()
logging_level = app_config['logging_level']

# Create a custom logger
file_name = __file__.split(os.sep)[-1]
logger = logging.getLogger(__name__)
logging.basicConfig(level=eval(logging_level), format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


r_handler = logging.handlers.RotatingFileHandler(filename=f"{log_dir}/{portfolio_id}.log", maxBytes=5 * 1024 * 1024, backupCount=150)
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
r_handler.setFormatter(f_format)
logger.addHandler(r_handler)

logger.warning('start ...')
symbol = app_config['symbol']

def round_to_increment(value: float, increment: int = 5) -> int:
    """
    Round a value to the nearest multiple of 'increment'.
    Example: round_to_increment(123, 5) -> 125
             round_to_increment(122, 5) -> 120
    """
    return round(value / increment) * increment

def format_yyyymmdd(date_obj):
    """
    Convert a datetime.date (or datetime.datetime) to yyyymmdd string.
    """
    return date_obj.strftime("%Y%m%d")

def next_business_day(start_date=None):
    """
    Return the next business day after start_date.
    Skips weekends only (Saturday/Sunday).
    """
    if start_date is None:
        start_date = datetime.date.today()

    next_day = start_date + datetime.timedelta(days=1)

    # If Saturday → skip to Monday
    if next_day.weekday() == 5:
        next_day += datetime.timedelta(days=2)

    return next_day


# ####
# Start IB
# ######

def get_closest_expiry_and_atm_strike():# --- Step 1: Define SPX underlying ---
    underlying = Index('SPX', 'CBOE')  # SPX is the underlying for SPXW
    ib.qualifyContracts(underlying)

    # --- Step 2: Request option chain info ---
    chains = ib.reqSecDefOptParams('SPX', '', 'IND', underlying.conId)

    # SPXW is a weekly trading class for SPX index options
    chain = next(c for c in chains if c.tradingClass == 'SPXW')

    # --- Step 3: Get current SPX price ---
    ticker = ib.reqMktData(underlying)
    ib.sleep(2)
    underlying_price = ticker.last or ticker.close
    logger.info(f"SPX current price: {underlying_price}")

    # --- Step 4: Choose expiry ---
    expiry = sorted(chain.expirations)[0]   # nearest expiry
    logger.info(f"Nearest expiry: {expiry}")

    # --- Step 5: Find ATM strike ---
    strikes = sorted(chain.strikes)
    atm_strike = min(strikes, key=lambda s: abs(s - underlying_price))

    logger.info(f"ATM Strike:{atm_strike}")
    return expiry, atm_strike

def create_call_and_contracts(expiry, strike):
    # --- Step 5: Create Option contracts (Call & Put) ---
    call_contract = Option('SPX', expiry, strike, 'C', 'CBOE', tradingClass='SPXW')
    put_contract = Option('SPX', expiry, strike, 'P', 'CBOE', tradingClass='SPXW')

    ib.qualifyContracts(call_contract, put_contract)
    logger.info(f"in create_call_and_contracts, call_contract: {call_contract}")
    logger.info(f"in create_call_and_contracts, put_contract: {put_contract}")
    return call_contract, put_contract

def get_asks(call_contract, put_contract):
    call_ticker = ib.reqMktData(call_contract,'', False, False)
    put_ticker = ib.reqMktData(put_contract,'', False, False)

    # Wait for data to populate
    ib.sleep(2)

    # --- Step 7: Extract ask prices ---
    logger.info(f"call_ticker: {call_ticker}")
    logger.info(f"put_ticker: {put_ticker}")
    call_ask = call_ticker.ask
    put_ask = put_ticker.ask

    logger.info(f"CALL Ask: {call_ask}")
    logger.info(f"PUT  Ask: {put_ask}")

    return call_ask, put_ask

def check_conditions(call_ask, put_ask):
    can_close = False
    logger.info(f"user_input_dic: {user_input_dic}")
    base_atm_straddle = user_input_dic.get('base_atm_straddle',-1) # used in condition
    contracts = user_input_dic.get('contracts',-1)  # used in condition
    multiplier = user_input_dic.get('multiplier', -1)  # used in condition
    strike = user_input_dic.get('strike' ,-1)  # used in condition

    #logger.info(f"user_input_dic: {json.dump(user_input_dic, inden=2)}")
    # logger.info(f"user_input_dic: {tabulate(user_input_dic, headers='keys', tablefmt='psql')}")

    condition = app_config['close_condition']
    condition_eval_result = eval(condition)
    logger.info(f"condition: {condition}")
    logger.info(f"condition_eval_result: {condition_eval_result}")
    if condition_eval_result:
        can_close = True

    return can_close

def close_option_positions(positions):

    for pos in positions:
        contract = pos.contract
        qty = pos.position

        if contract.secType == 'OPT' and qty != 0:
            # --- Step 2: Determine opposite action ---
            action = 'SELL' if qty > 0 else 'BUY'
            close_qty = abs(qty)

            # --- Step 3: Create market order to close ---
            order = MarketOrder(action, close_qty)
            order.orderRef = f"CLOSE-{u_run_number}"

            # --- Step 4: Place the order ---
            contract.exchange = 'SMART'  # or 'CBOE' if your account requires it
            trade = ib.placeOrder(contract, order)
            trade.fillEvent += on_fill
            ib.sleep(0.5)  # small delay to avoid pacing violations

            logger.info(f"trade: {trade}")
            # Convert to DataFrame automatically
            df = ib_util.df([trade])

            logger.info(f"close_option_positions, trade:\n{df.to_markdown()}")
            logger.info(f"Closing {contract.localSymbol}, action: {action}, close_qty: {close_qty}")

    return

def check_conditions_and_exit(positions):
    if not app_config['run_condition_checker']:
        return False

    expiry, atm_strike_price = get_closest_expiry_and_atm_strike()
    call_contract, put_contract = create_call_and_contracts(expiry, atm_strike_price)
    call_ask, put_ask = get_asks(call_contract, put_contract)
    can_close = check_conditions(call_ask, put_ask)
    logger.info(f"can_close: {can_close}")
    if can_close:
        close_option_positions(positions)
    return


def find_positions_to_monitor():
    positions = get_all_open_option_positions()
    logger.info(f"positions_to_monitor: \n{tabulate(positions, headers='keys', tablefmt='psql')}")
    ps = []
    for p in positions:
        logger.info(f"p: {p}")
        if p.contract.symbol == 'SPX' and p.contract.tradingClass == 'SPXW':
            logger.info(f"adding it to the list ...")
            ps.append(p)

    logger.info(f"in find_positions_to_monitor()")
    logger.info(f"\n{my_tabulate(ps)}")
    return ps

def get_all_open_option_positions():
    positions = ib.positions()

    # for pos in positions:
    #     contract = pos.contract
    #     if contract.secType == 'OPT':  # only options
    #         logger.info(
    #             f"Symbol: {contract.symbol:<5}",
    #             f"Expiry: {contract.lastTradeDateOrContractMonth}",
    #             f"Right: {contract.right}",
    #             f"Strike: {contract.strike}",
    #             f"Qty: {pos.position}",
    #             f"Avg Price: {pos.avgCost}"
    #         )

    logger.info(f"positions: \n{tabulate(positions, headers='keys', tablefmt='psql')}")
    return positions

def create_ib_connection():
    connected = False
    ib = None
    while not connected:
        try:
            ib = IB()
            ib.connect(ib_config['ip'], ib_config['port'], clientId=ib_config['client_id'], timeout=0)
            connected = True
            logger.info(f"IB connected.")
        except Exception as e:
            # TODO needs better exception handling
            logger.error(f"error: {e}")
            import traceback

            logger.info(traceback.format_exc())
            time.sleep(60)
    return ib
def get_current_price(symbol='SPX'):
    spx = Index(symbol='SPX', exchange='CBOE', currency='USD')
    ib.qualifyContracts(spx)

    # Request market data
    ticker = ib.reqMktData(spx, '', False, False)

    ib.sleep(2)  # give IB time to send data
    logger.info(f"SPX last: {ticker.last},  bid:, {ticker.bid},  ask:{ticker.ask}")
    last_price = ticker.last
    if np.isnan(last_price):
        last_price = -1
    else:
        last_price = round_to_increment(last_price, 5)
    return last_price


def create_option_contract(strike, expiry, right, exchange="CBOE", symbol='SPX', trading_class='SPXW'):
    global contracts
    # put in the loop
    contract = Option(
        symbol=symbol,
        lastTradeDateOrContractMonth=expiry,
        strike=strike,
        right=right,
        exchange=exchange,
        tradingClass=trading_class
    )
    contracts.append(contract)

    logger.info(f"calling qualifyContracts : ")
    ib.qualifyContracts(*contracts)
    logger.info("qualifyContracts is done.")
    return

def send_order():
    global contracts
    total_quantity = 1
    # for
    for contract in contracts:
        order = MarketOrder('BUY', totalQuantity=total_quantity)
        order.orderRef = f"OPEN-{u_run_number}"
        trade = ib.placeOrder(contract, order)
        trade.fillEvent += on_fill
        ib.sleep(1)
        logger.info(f"Order sent ....")
        logger.info(trade)

    return

def has_open_option_positions():
    # Get all current positions
    positions = ib.positions()

    for pos in positions:
        contract = pos.contract
        position = pos.position

        if position == 0:
            continue  # already flat

        # Ensure the contract has an exchange # and not contract.exchange
        # I commented it ...
        if isinstance(contract, Option) :
            # TODO for now we dont send any order if we have open order
            # TODO we can send bu monitoring and close does not support it ...
            # but in case only we have one open option which is not executed, we will not be able to send ...

            if contract.lastTradeDateOrContractMonth == screening_expiry:
                logger.warning(f"@@@ check_for_open_option_positions, There is at least one open option ...screening_expiry: {screening_expiry}, contract: {contract}")
                return True
    return False
    create_option_contract()

def sleep_enough():
    run_spend_time = round(end_time - start_time, 2)
    run_should_take = app_config['run_should_take_seconds']
    need_sleep_seconds = 0
    if run_spend_time < run_should_take:
        need_sleep_seconds = run_should_take - run_spend_time
    logger.warning(f'{run_number}) {u_run_number}, run_spend_time: {run_spend_time} seconds, run_should_take: {run_should_take}')
    time.sleep(need_sleep_seconds)
    return

def run_should_take_seconds():
    return app_config['run_should_take_seconds']

def update_config_and_save(config, key, value):
    global app_config
    existing_value = app_config[key]
    if value != existing_value:
        logger.info(f"in update_config_and_save, key: {key}, existing value: {existing_value}, new value: {value} ")
        app_config = reload_app_config()
        app_config[key] = value
        file = f'{configs_folder}/config-{portfolio_id}.yaml'
        with open(file, 'w') as f:
            yaml.dump(app_config, f)
    return

def flatten(obj, prefix=''):
    """
    Recursively flatten an object (like Fill, Execution, CommissionReport) into a dict.
    """
    result = {}
    for attr in dir(obj):
        if attr.startswith('_') or callable(getattr(obj, attr)):
            continue
        value = getattr(obj, attr)
        if hasattr(value, '__dict__'):
            # nested object → recurse
            result.update(flatten(value, prefix=f'{prefix}{attr}_'))
        else:
            result[f'{prefix}{attr}'] = value
    return result

def get_executed_orders_from_ib_and_save_ver2():
    # IB has only for 24 hrours ... so we need to save it ofter ...
    file = executed_orders_from_ib_ver_2_file_path
    df = pd.DataFrame()

    now = datetime.datetime.now()
    yesterday = now - datetime.timedelta(days=3)

    exec_filter = ExecutionFilter(
        time=yesterday.strftime('%Y%m%d %H:%M:%S')  # format: YYYYMMDD HH:MM:SS
    )
    execs = ib.reqExecutions(exec_filter)
    i = 0

    for trade in execs:
        i = i + 1
        if i < 2:
            logger.info(f"get_executed_orders_from_ib_and_save(), trade: {trade}")

        flatten_dic = flatten(trade)
        logger.info(f"in get_executed_orders_from_ib_and_save_ver2, :flatten :{flatten_dic}")
        df = pd.concat([df, pd.DataFrame([flatten_dic])], ignore_index=True)
        #logger.info(f"df:\n {df.to_markdown()}")

    df.to_csv(file, index=False, header=not os.path.exists(file), mode='a')
    drop_dupplicates(file, )
    write_file_in_tabulate(file)
    return df

def on_fill(trade, fill):
    global flatten_fill_df
    global flatten_trade_df

    logger.warning(f'in on_fill, trade: {trade}')
    logger.warning(f'in on_fill, fill: {fill}')
    logger.warning(f'in on_fill, fill.execution.order_id: {fill.execution.orderId}, fill.contract.symbol: {fill.contract.symbol}')


    flatten_dic = flatten(fill)
    logger.info(f":flatten :{flatten_dic}")
    flatten_fill_df = pd.concat([flatten_fill_df, pd.DataFrame([flatten_dic])], ignore_index=True)
    #logger.info(f"flatten_fill_df:\n {flatten_fill_df.to_markdown()}")

    flatten_dic = flatten(trade)
    logger.info(f":flatten :{flatten_dic}")
    flatten_trade_df = pd.concat([flatten_trade_df, pd.DataFrame([flatten_dic])], ignore_index=True)
    #logger.info(f"flatten_trade_df:\n {flatten_trade_df.to_markdown()}")

    df = ib_util.df([trade])
    logger.info(f"on_fill, trade:\n{df.to_markdown()}")

    df = ib_util.df([fill])
    logger.info(f"on_fill, fill:\n{df.to_markdown()}")

    return

def write_file_in_tabulate(src_file_path, dest_file_path= None):

    df = pd.read_csv(src_file_path)
    if len(df) > 0:
        if dest_file_path is None:
            dest_file_path = f"{src_file_path}-txt.csv"
        # Convert only object and bool columns to string (vectorized)
        # FIXME not happy to do that as may affect performance ...
        # for col in df.select_dtypes(include=['object', 'bool']):
        #     df[col] = df[col].astype(str)
        with open(dest_file_path, 'w') as f:
            f.write(tabulate(df.astype(str), headers='keys', tablefmt='psql'))
    return

def save_df_to_file(df=None, file='', mode='w'):
    if len(df) > 0:
        if not '/' in file:
            file = f'{intermediate_dir}/{file_name}'
        df.to_csv(file, mode=mode, index=False)  # , header=not os.path.exists(file),index=False
        drop_dupplicates(file)  # 'event'
        write_file_in_tabulate(src_file_path=file)
    return

def get_all_open_orders():
    open_orders = ib.reqAllOpenOrders()
    return open_orders

def drop_dupplicates(file_path, unique_column=None, keep='last'):
    # Drop dupplicaes
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        if unique_column is None:
            df = df.drop_duplicates(keep=f'{keep}')
        else: # has fields ...
            df = df.drop_duplicates(subset=[f'{unique_column}'], keep=f'{keep}')
        df.to_csv(file_path, index=False, mode='w')
    return
def cancel_open_orders(symbol):
    if not app_config['cancel_open_orders_on_start']:
        return
    open_orders = ib.reqAllOpenOrders()
    # Cancel all open orders
    for order in open_orders:
        logger.info('----')
        logger.warning(f"Canceling open order, order_id: {order.order.orderId}, order: {order}")
        contract = order.contract

        if not isinstance(contract, Option):
            logger.warning(f"it is NOT an option!!!")
        else:
            logger.warning(f"it is an option!!!")
            if order.contract.symbol == symbol:
                trade = ib.cancelOrder(order.order)
                logger.warning(f"open order canceled, trade: {trade}")
                while not trade.isDone():
                    logger.warning(f"sleep until is done, trade.isDone(): {trade.isDone()}")
                    ib.sleep(0.5)
            else:
                logger.warning(f"in cancel_all_open_orders, not canceling order.contract.symbol: {order.contract.symbol}")
    return

def load_ib_config():
    logger.warning(f"loading app_config ....")
    app_config = miscutils.load_config(f'{configs_folder}/ib-config.yaml')
    logger.info(f"loaded.")
    return app_config

def load_csv_to_df(file):
    if os.path.exists(file):
        df = pd.read_csv(file)
        return df
    else:
        return pd.DataFrame()


def my_tabulate(x):
    try:
        return tabulate(x, headers='keys', tablefmt='psql')
    except Exception as e:
        logger.error(f"e:{e}")
        logger.warning(f" type: {type(x)}")
        return "Error in tabular ..."


def dump_application_state_to_file():
    file_path = application_state_file_path
    with open(file_path, 'w') as f:
        logger.info(f"saving at file_path: {file_path} , application_state: {application_state} ")
        json.dump(application_state, f, indent=4)
        logger.info(f"saving done. ")

    return

def load_application_state_from_file():
    global application_state
    file_path = application_state_file_path
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            logger.info(f"loading from file_path: {file_path} ")
            application_state = json.load(f)
        logger.info(f"loaded, application_state: {application_state}")
    return

def print_application_state(application_state, msg = ''):

    logger.warning(f"{msg}\n{pprint.pformat(application_state)}")
    return

def has_open_trade(type='option'):
    return False


def update_config_and_save(config, key, value):
    global app_config
    existing_value = app_config[key]
    if value != existing_value:
        logger.info(f"in update_config_and_save, key: {key}, existing value: {existing_value}, new value: {value} ")
        app_config = reload_app_config()
        app_config[key] = value
        file = f'{configs_folder}/config-{portfolio_id}.yaml'
        with open(file, 'w') as f:
            yaml.dump(app_config, f)
    return
def open_order_if_not_exists():
    # if not has_open_trade(type='option'):
    if app_config['open_position']:
        logger.info(f"in open_order_if_not_exists, ")
        update_config_and_save(app_config,'open_position' , False)
        expiry = format_yyyymmdd(next_business_day())
        # current_price = 6710
        right = 'C'
        create_option_contract(strike=current_price, expiry=expiry, right=right)  # adds to contracts
        right = 'P'
        create_option_contract(strike=current_price, expiry=expiry, right=right) # adds to contracts

        send_order()

    return

def read_user_input_from_shared_folder():
    file_path = user_input_file_path
    user_input_dic = {}
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            logger.info(f"loading from file_path: {file_path} ")
            user_input_dic = json.load(f)
        logger.info(f"loaded, user_input_dic: {user_input_dic}")
    return user_input_dic


if __name__ == "__main__":
    ib_config = load_ib_config()
    ib = create_ib_connection()
    application_state = {}
    contracts = [] # This is for creating ...
    flatten_fill_df = load_csv_to_df(flatten_fill_file_path)
    flatten_trade_df = pd.DataFrame()

    consequence_exception = 0
    running_loop = True
    run_number = 0
    while running_loop:
        try:
            start_time = time.time()
            run_number += 1
            now = datetime.datetime.now()
            date_yyyy_mm_dd = now.strftime("%Y-%m-%d")
            date_yyyy_mm_dd_w_time = now.strftime("%Y-%m-%d %H:%M:%S")
            run_date_time = now.strftime("%Y-%m-%d__%H-%M-%S")
            u_run_number = f"{now.strftime('%Y%m%d-%H%M%S')}--{run_number}"
            logger.info(f"==================== run_number: {run_number}  run_date_time: {run_date_time}:  u_run_number: {u_run_number}")
            app_config = load_app_config()
            current_price = get_current_price()

            open_order_if_not_exists()

            # get_all_open_option_positions()
            user_input_dic = read_user_input_from_shared_folder()

            positions_to_monitor = find_positions_to_monitor()
            check_conditions_and_exit(positions_to_monitor)
            time.sleep(10)


            dump_application_state_to_file()
            print_application_state(application_state)
            end_time = time.time()
            sleep_enough()

        except Exception as e:
            consequence_exception = consequence_exception + 1
            logger.error(f"X error: {e}")
            import traceback
            print(traceback.format_exc())
            time.sleep(60)


            if consequence_exception == 3:
                # email_util_ver_02.send_email('saeed.bx1@yahoo.com', f'error in {p_id}', body = f"{e}<br\><br\><br\>{traceback.format_exc()}")
                pass
            if isinstance(e, ConnectionError):
                # set a flag and set connection in loop .. exists if riase exceptin
                logger.error("It's a ConnectionError, try to reconnect ")
                ib = create_ib_connection()
                logger.warning("Done.")