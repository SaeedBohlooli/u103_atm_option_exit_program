from trading_utils import *
import logging
logger = logging.getLogger(__name__)
import sys
sys.path.insert(0, f'../')

from trading_core.ws_server import WSServer
from trading_core.streamers.state_streamer import StateStreamer
from trading_core.streamers.config_streamer import ConfigStreamer
from trading_core.ib_connector import IBConnector
from trading_core.file_manager import FileManager
from trading_core.market_data_store import MarketDataStore
from trading_core import user_request_loop

from trading_utils import user_request_fetcher
from trading_utils import user_request_router
from trading_utils import position_router
from trading_utils import order_router

from trading_utils import ib_pricing_async
from trading_utils import date_utils

from trading_engine import options_helper
from trading_engine import pricing_helper
from trading_engine import application_state_helper
from trading_engine import user_request_helper

class TradingEngine:

    def __init__(self, boot):
        self.boot = boot
        self.logger = boot.logger
        self.app_config = boot.app_config
        self.application_state = boot.application_state
        self.ws = WSServer(host="0.0.0.0", port=self.app_config.get('ws_port', 6106))
        self.runtime = boot.runtime
        self.market_data = MarketDataStore()


    # --------------------------
    # BELOW ARE YOUR LOOP HANDLERS
    # --------------------------

    async def engine_loop(self, ib):
        run_number = 0
        initial_setup = False
        application_state_helper.init_application_state(self.application_state)

        atm_straddle_tracker_df = pd.DataFrame()
        while True:
            try:
                start_time = time.time()
                run_number += 1
                current_hh_mm_ny = self.runtime.now_hhmm()
                current_date_time_ny = self.runtime.now_Y_M_D_H_S()
                unique_run_number =  self.runtime.generate_unique_run_number(run_number)
                self.app_config = self.runtime.reload_config()
                self.application_state['current_date_time_ny'] = current_date_time_ny
                self.application_state['current_hh_mm_ny'] = current_hh_mm_ny
                self.application_state['unique_run_number'] = unique_run_number

                logger.warning(f"==================== unique_run_number: {unique_run_number}, current_hh_mm_ny: {current_hh_mm_ny}")
                if ib is None:
                    logger.warning("ib is None... so gie a try to reconnect ...")
                    await asyncio.sleep(3)
                    continue
                symbol = 'SPX'
                option_class = 'SPXW'

                symbol_price = self.application_state.get('symbols', {}).get(symbol, {}).get('current_price', None)
                logger.info(f"symbol_price: {symbol_price} ")
                if symbol_price is None or symbol_price == -1 or np.isnan(symbol_price):
                    logger.info(f"@@ Waiting for valid SPX price...symbol_price: {symbol_price}")
                    await asyncio.sleep(1)
                    continue

                atm_strike = options_helper.get_atm_strike_price(self.application_state, symbol, symbol_price)
                expiry = self.runtime.now_YYYYMMDD()
                self.application_state.setdefault('user_input', {})['expiry'] = expiry

                call_contract = await options_helper.create_spx_option_contract(ib, self.app_config, self.application_state, option_class, expiry, atm_strike, 'C')
                put_contract = await options_helper.create_spx_option_contract(ib, self.app_config, self.application_state, option_class, expiry, atm_strike, 'P')
                logger.info(f"@@ call_contract: {call_contract} ")
                logger.info(f"@@ put_contract: {put_contract} ")
                logger.info(f"@@ atm_strike: {atm_strike} for symbol_price: {symbol_price}")
                if not initial_setup:
                    initial_setup = True
                    # initial tasks can be placed here
                quotes_df = await pricing_helper.get_bid_ask_for_contracts(ib, self.app_config, self.application_state, [call_contract, put_contract])
                atm_straddle_tracker_df = options_helper.calualte_misc_metrics(self.app_config, self.application_state, atm_strike, quotes_df, atm_straddle_tracker_df)
                logger.info(f"@@ atm_straddle_tracker_df:  \n{atm_straddle_tracker_df.to_markdown()}")
                atm_straddle_tracker_obj_wrapper = options_helper.create_straddle_tracker_wrapper_object(self.app_config, self.application_state, atm_strike, atm_straddle_tracker_df)
                if self.app_config.get('overwrite_atm_straddle_tracker_obj_wrapper', True):
                    self.application_state['atm_straddle_tracker_obj_wrapper'] = atm_straddle_tracker_obj_wrapper

                position_router.update_application_state_for_ib_positions(ib, self.application_state)
                await order_router.update_application_state_for_ib_open_orders(ib,self.app_config, self.application_state)

                from pprint import pprint
                logger.info(f"@@ atm_straddle_tracker_obj_wrapper:  \n{pprint(atm_straddle_tracker_obj_wrapper)}")


                # elf.application_state['atm_straddle_tracker_obj_wrapper'] = {'x': 1}
                #custom_option_data_map = options_helper.convert_to_map_ready_for_stream(custom_option_data, self.app_config, self.application
                #


                # self.application_state.setdefault('symbols', {}).setdefault('SPX', {})['option_chain'] = bid_ask_for_c_and_p_map
                # custom_option_data.append(bid_ask_for_c_and_p_map)




                self.application_state['global_state.symbol_to_conid'] = global_state.symbol_to_conid
                self.application_state['global_state.conid_to_symbol'] = global_state.conid_to_symbol
                self.application_state['global_state.option_contract_cache_len'] = len(global_state.option_contract_cache)

                end_time = time.time()
                run_spend_time = round(end_time - start_time, 2)
                logger.warning(f'==================== unique_run_number: {unique_run_number}, run_spent_time: {run_spend_time} seconds, no sleep ...')

                await asyncio.sleep(self.app_config['interval_seconds']['engine_loop'])
            except Exception as e:
                logger.warning(f"@@@ Unexpected error in engine_loop: {e}")
                logger.error(f"@@@ error: {traceback.format_exc()}" )
                await asyncio.sleep(self.app_config['interval_seconds']['engine_loop'])

    async def spx_price_stream_loop(self, ib, interval_sec=2):

        while True:
            try:
                spx_current_price = await ib_pricing_async.get_or_subscribe_symbol_price(ib, "SPX")
                self.application_state.setdefault('symbols', {}).setdefault('SPX', {})['current_price'] = spx_current_price

                packet = {
                    "type": "tick",
                    "symbol": "SPX",
                    "price": spx_current_price,
                    "timestamp": time.time(),
                }
                logger.info("[spx_price_stream_loop] streaming ....")
                await self.ws.broadcast(packet)
                logger.info("[spx_price_stream_loop]  streamed.")
                await asyncio.sleep(interval_sec)
                logger.info(f"spx_price_stream_loop in the streem loop  spx_current_price: {spx_current_price} ")
            except Exception as e:
                logger.warning(f"Unexpected error in spx_price_stream_loop: {e}")
                await asyncio.sleep(interval_sec)



    async def run(self):
        logger.info("Starting Trading Engine")
        ib = await IBConnector.connect_from_config(self.app_config)

        ws_server = await self.ws.start()

        state_streamer = StateStreamer(self.app_config, self.application_state, self.ws, interval=5)
        config_streamer = ConfigStreamer(self.app_config, self.application_state, self.ws, interval=12)

        self.logger.info("WebSocket server is starting...")

        await asyncio.gather(
            ws_server,
            state_streamer.run(),
            config_streamer.run(),
            self.spx_price_stream_loop(ib, interval_sec=5),
            self.engine_loop(ib),
            user_request_loop.fetch_user_request_loop(self.app_config, self.application_state,interval_sec=5),
            user_request_loop.process_common_user_request_loop(ib, self.app_config, self.application_state,interval_sec=5),
            user_request_helper.process_app_user_request_loop(ib, self.app_config, self.application_state,interval_sec=5),
            self.boot.data_saver_manager.run(ib, interval_sec=60),
        )