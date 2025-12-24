import logging
logger = logging.getLogger(__name__)

def setup_order(ib,app_config,application_state):
    atm_straddle_tracker_obj_wrapper = application_state.get('atm_straddle_tracker_obj_wrapper')
    if not atm_straddle_tracker_obj_wrapper:
        logger.warning(f"x(), atm_straddle_tracker_obj_wrapper not found in application_state.")
        return None

    order_setup_input = application_state.get('user_input', {}).get('order_setup', {})
