import asyncio
import logging
import traceback

logger = logging.getLogger(__name__)
from trading_engine import order_setup_helper
async def process_user_requests(ib, app_config, application_state):
    user_request: object
    for user_request in application_state.get('user_requests', []):
        logger.info(f"Processing {user_request.get('request_type', '')} user_request: {user_request}")
        request_type = user_request.get('request_type', '')
        if 'ENGINE_PROCESSED' in user_request.get('status', ''):
            continue
        if request_type.upper() == 'SETUP_ORDER':
            logger.info(f"Processing SETUP_ORDER user_request: {user_request}")
            # Add your ORDER_SETUP processing logic here
            await order_setup_helper.setup_order(ib, app_config, application_state, user_request)

            user_request['status'] += '|ENGINE_PROCESSED'




async def process_app_user_request_loop(ib, app_config, application_state, interval_sec=5):
    while True:
        try:
            logger.info("process_app_user_request_loop...")
            await process_user_requests(ib, app_config, application_state)
            await asyncio.sleep(interval_sec)
        except Exception as e:
            logger.warning(f"@@@ process_app_user_request_loop Unexpected error: {e}")
            logger.error(f"@@@ process_app_user_request_loop error: {traceback.format_exc()}" )
            await asyncio.sleep(interval_sec)