
import logging

import pandas as pd

logger = logging.getLogger(__name__)
from trading_utils import ib_contract, ib_pricing_async


def get_atm_strike_price(application_state, symbol, symbol_price):
    atm = round(symbol_price / 5) * 5
    application_state['symbols'][symbol]['atm_strike'] = atm
    logger.info(f"Calculated ATM strike for {symbol}: {atm} based on price {symbol_price}")
    return atm

async def  create_spx_option_contract(ib, app_config, application_state, symbol, expiry, strike, right):
    from trading_utils import ib_contract
    qc = await ib_contract.get_option_contract_cached(ib,symbol, expiry, strike, right)

    return qc


def calualte_misc_metrics(app_config, application_state, atm_strike, quotes_df, atm_straddle_tracker_df):
    symbol = application_state.get('user_input',{}).get('option_class', 'SPX')

    call_tick_info_map = ib_pricing_async.find_bid_ask(quotes_df, symbol, atm_strike, right='C')
    put_tick_info_map = ib_pricing_async.find_bid_ask(quotes_df, symbol, atm_strike, right='P')
     # = application_state.setdefault('atm_straddle_tracker', {})
    row = {'timestamp': call_tick_info_map.get('timestamp'),  'symbol': symbol, 'symbol_price': atm_strike, 'atm_strike': atm_strike,
           'call_bid': call_tick_info_map.get('bid'), 'call_ask': call_tick_info_map.get('ask'),
          'put_bid': put_tick_info_map.get('bid'), 'put_ask': put_tick_info_map.get('ask'),
           'sum_put_call_ask': (call_tick_info_map.get('ask', 0) + put_tick_info_map.get('ask', 0)),
           'difference': 0, 'x_diffs_total': 0, 'call_spread': 0, 'put_spread': 0}

    atm_straddle_tracker_df = pd.concat([atm_straddle_tracker_df, pd.DataFrame([row])], ignore_index=True)

    cols = ["call_bid", "call_ask", "put_bid", "put_ask"]
    logger.info(f"Dropping rows with all NaNs in columns {cols} len(atm_straddle_tracker_df) before: {len(atm_straddle_tracker_df)}")
    atm_straddle_tracker_df = atm_straddle_tracker_df.dropna(subset=cols, how="all")
    logger.info(f"Dropping rows with all NaNs in columns {cols} len(atm_straddle_tracker_df) after: {len(atm_straddle_tracker_df)}")

    return atm_straddle_tracker_df

def create_straddle_tracker_wrapper_object(app_config, application_state, atm_strike, atm_straddle_tracker_df):
    # atm_straddle_tracker_df = atm_straddle_tracker_df.
    straddle_tracker = {
        'symbol': application_state.get('user_input', {}).get('option_class', 'SPX'),
        'atm_strike': atm_strike,
        'day_highest_atm_strike':  int(v) if pd.notna(v := atm_straddle_tracker_df['atm_strike'].max()) else 0,
        'last_atm_strike':         int(v) if len(atm_straddle_tracker_df) > 0 and pd.notna(v := atm_straddle_tracker_df['atm_strike'].iloc[-1]) else 0,
        'diff_high_base': 0,
        'diff_base_last': 0,
        'call_spread_max':0,
        'put_spread_max':0,
        'call_spread_min':0,
        'put_spread_min':0,
        'call_spread_latest':0,
        'put_spread_latest':0,
        'records': atm_straddle_tracker_df.to_dict('records')
    }
    return straddle_tracker