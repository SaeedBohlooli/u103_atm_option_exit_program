import logging
logger = logging.getLogger(__name__)
from trading_engine import position_helper
from trading_utils import ib_pricing_async
from trading_utils import ib_positions_async
from trading_utils import ib_orders_async

async def setup_order(ib,app_config,application_state, user_request ):
    symbol = application_state.get('use_input', {}).get('symbol')

    atm_straddle_tracker_obj_wrapper = application_state.get('atm_straddle_tracker_obj_wrapper')
    if not atm_straddle_tracker_obj_wrapper:
        logger.warning(f"x(), atm_straddle_tracker_obj_wrapper not found in application_state.")
        # return None
    last_x_diff_total = atm_straddle_tracker_obj_wrapper.get("last_x_diff_total") # TODO need tto create it if not found
    day_highest_atm_strike = atm_straddle_tracker_obj_wrapper.get("day_highest_atm_strike")  # F
    atm_trigger = user_request.get('atm_trigger')  # a
    user_input_spx_price_trigger = user_request.get('spx_price_trigger')  # b
    base_atm_trigger = user_request.get('base_atm_trigger')  # c

    current_price = await ib_pricing_async.get_or_subscribe_symbol_price(ib, symbol)  # used in config

    # order_setup_input = application_state.get('user_input', {}).get('order_setup', {})
    for order in user_request.get('orders',[]):
        logger.info(f"Processing order: {order}")
        user_input_entry_spx_price = order.get('entry_spx_price') # d
        user_input_base_atm_price = order.get('base_atm_price')  #  e
        contracts = order.get('contracts')  # f
        right = order.get('option_type')  # g
        close_short_strike = order.get('close_short_strike') # h
        close_long_strike = order.get('close_long_strike')  # i
        if user_input_entry_spx_price is None:
            logger.warning(f"  entry_spx_price not found in order: {order}")
            continue
        if close_long_strike is None:
            logger.warning(f"  close_long_strike not found in order: {order}")
            continue
        if close_short_strike is None:
            logger.warning(f"  close_short_strike not found in order: {order}")
            continue
        has_long_open_position, con_id = position_helper.is_open_position_with_strike(application_state, strike=close_long_strike, side='long')
        if has_long_open_position:
            logger.info(f"  Found open long position with strike: {close_long_strike}, proceeding to close it.")

            for cond_name, rules in app_config["order_setup"]["conditions"].items():
                logger.info(f"Evaluating {cond_name}")
                results= []
                for rule in rules:
                    logger.info(f"  rule: {rule}")
                    check = eval(rule)
                    logger.info(f"    Condition {cond_name} with rule: {rule}")
                    results.append(check)

                if all(results):
                    logger.info(f"    All conditions met for {cond_name}, placing order.")
                    order_ref = ib_orders_async.generate_order_ref(portfolio_id=application_state.get('portfolio_id'), event='CLOSE', symbol=symbol, unique_run_number=application_state.get('unique_run_number'))
                    ib_positions_async.close_position_by_con_id(ib, con_id=con_id, order_ref=order_ref)
                        # Place order logic here


