import logging
logger = logging.getLogger(__name__)
from trading_engine import position_helper
from trading_utils import ib_pricing_async
from trading_utils import ib_positions_async
from trading_utils import ib_orders_async

async def setup_order(ib,app_config,application_state, user_request ):
    symbol = application_state.get('user_input', {}).get('symbol')
    ib_open_orders = application_state.get('ib_open_orders', [])
    atm_straddle_tracker_obj_wrapper = application_state.get('atm_straddle_tracker_obj_wrapper')
    if not atm_straddle_tracker_obj_wrapper:
        logger.warning(f"x(), atm_straddle_tracker_obj_wrapper not found in application_state.")
        # return None
    last_x_diffs_total = atm_straddle_tracker_obj_wrapper.get("last_x_diffs_total", 0) # TODO need tto create it if not found
    day_highest_atm_strike = atm_straddle_tracker_obj_wrapper.get("day_highest_atm_strike")  # F
    atm_trigger = user_request.get('atm_trigger')  # a
    user_input_spx_price_trigger = user_request.get('spx_price_trigger')  # b
    base_atm_trigger = user_request.get('base_atm_trigger')  # c
    current_price = await ib_pricing_async.get_or_subscribe_symbol_price(ib, symbol)  # used in config
    # put all above variables into a dict for eval

    vars = {
        'web_request_id': user_request.get('web_request_id'),
        'last_x_diffs_total': last_x_diffs_total,
        'day_highest_atm_strike': day_highest_atm_strike,
        'atm_trigger': atm_trigger,
        'user_input_spx_price_trigger': user_input_spx_price_trigger,
        'base_atm_trigger': base_atm_trigger,
        'current_price': current_price }
    # order_setup_input = application_state.get('user_input', {}).get('order_setup', {})
    i = 0
    for order in user_request.get('orders',[]):
        i += 1
        logger.info(f"Processing order: {order}")
        user_input_entry_spx_price = order.get('entry_spx_price') # d
        user_input_base_atm_price = order.get('base_atm_price')  #  e
        contracts = order.get('contracts')  # f
        right = order.get('option_right')  # g
        close_short_strike = order.get('close_short_strike') # h
        close_long_strike = order.get('close_long_strike')  # i
        cancel_short_strike_combo = order.get('cancel_short_strike_combo') #k
        cancel_long_strike_combo = order.get('cancel_long_strike_combo') #l
        cancel_short_strike_single_leg = order.get('cancel_short_strike_single_leg')  # m
        cancel_long_strike_single_leg = order.get('cancel_long_strike_single_leg') #n
        # add them to vars
        # put them in different variable names to avoid confusion
        d = {
            'user_input_entry_spx_price': user_input_entry_spx_price,
            'user_input_base_atm_price': user_input_base_atm_price,
            'contracts': contracts,
            'right': right,
            'close_short_strike': close_short_strike,
            'close_long_strike': close_long_strike,
            'cancel_short_strike_combo': cancel_short_strike_combo,
            'cancel_long_strike_combo': cancel_long_strike_combo,
            'cancel_short_strike_single_leg': cancel_short_strike_single_leg,
            'cancel_long_strike_single_leg': cancel_long_strike_single_leg,
            'memo': '',
        }
        vars[i] = d
        application_state['vars']  = vars
        if user_input_entry_spx_price is None:
            logger.warning(f"  entry_spx_price not found in order: {order}")
            d['memo'] += '|entry_spx_price missing'
            continue
        if close_long_strike is None:
            logger.warning(f"  close_long_strike not found in order: {order}")
            d['memo'] += '|close_long_strike missing'
            continue
        # if close_short_strike is None:
        #     logger.warning(f"  close_short_strike not found in order: {order}")
        #     continue
        has_long_open_position, con_id = position_helper.is_open_position_with_strike(application_state, symbol, strike=close_long_strike, side='long')
        if has_long_open_position:
            logger.info(f"  Found open long position with strike: {close_long_strike}, proceeding to close it.")
            d['memo'] += '|found_long_position'
            for cond_name, rules in app_config["order_setup"]["conditions"].items():
                logger.info(f"Evaluating {cond_name}")
                results= []
                for rule in rules:
                    logger.info(f"  rule: {rule}")
                    check = bool(eval(rule))
                    logger.info(f"    Condition {cond_name} with rule: {rule}, {check}")
                    results.append(check)
                    d[rule] = check

                if all(results):
                    logger.info(f"    All conditions met for {cond_name}, placing order.")
                    d['memo'] += f'|{cond_name}_conditions_met'
                    d[cond_name] = True
                    order_ref = ib_orders_async.generate_order_ref(portfolio_id=application_state.get('portfolio_id'), event='CLOSE', symbol=symbol, unique_run_number=application_state.get('unique_run_number'))
                    ib_positions_async.close_position_by_con_id(ib, con_id=con_id, order_ref=order_ref)
                    break # as it closed we can break here
                else:
                    logger.info(f"    Not all conditions met for {cond_name}, skipping order.")
                    d['memo'] += f'|{cond_name}_conditions_not_met'
                    d[cond_name] = False


                        # Place order logic here


        else:
            d['memo'] += '|no_long_position'
            logger.info(f"  No open long position with strike: {close_long_strike}")


        for strike_for_cancel in [cancel_long_strike_single_leg]:
            for ib_order in ib_open_orders:
                order_symbol = ib_order.get('symbol')
                order_strike = ib_order.get('strike')
                order_right = ib_order.get('right')
                order_status = ib_order.get('status')
                order_action = ib_order.get('action')
                if ( order_symbol == symbol and
                        order_strike == strike_for_cancel and
                        order_action in ['BUY']):
                    logger.info(f"  Cancelling single leg order with strike: {strike_for_cancel}, right: {order_right}, status: {order_status}")
                    d['memo'] += f'|cancelling_single_leg_{strike_for_cancel}'
                    ib_orders_async.cancel_order_by_order_id(ib, order_id=ib_order.get('order_id'))


