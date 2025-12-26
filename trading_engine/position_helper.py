import logging
logger = logging.getLogger(__name__)


def is_open_position_with_strike(application_state, symbol, strike, side):
    for position in application_state.get("ib_positions", []):
        if position.get('symbol') == symbol and position.get('strike') == strike and position.get('side') == side:
            logger.info(f"is_open_position_with_strike: Found open position for {symbol} at strike {strike} on side {side}.")
            return True, position.get('contract_id')

    return False, None