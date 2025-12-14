
import logging
logger = logging.getLogger(__name__)

def open_order_if_not_exists(ib, app_config, application_state, current_price):
    # if not has_open_trade(type='option'):
    if app_config['open_position'] and not application_state.get('open_position'):
        logger.info(f"in open_order_if_not_exists, ")
        application_state['opened_position'] = True

         # create option contract at-the-money with nearest expiry
        expiry = format_yyyymmdd(next_business_day())
        # current_price = 6710
        right = 'C'
        create_option_contract(strike=current_price, expiry=expiry, right=right)  # adds to contracts
        right = 'P'
        create_option_contract(strike=current_price, expiry=expiry, right=right) # adds to contracts

        send_order()

    return