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

from trading_utils import user_request_fetcher
from trading_utils import user_request_router
from trading_utils import position_helper
from trading_engine import options_helper

class TradingEngine:

    def __init__(self, boot):
        self.boot = boot
        self.logger = boot.logger
        self.app_config = boot.app_config
        self.application_state = boot.application_state
        self.ws = WSServer(host="0.0.0.0", port=self.app_config.get('ws_port', 6106))
        self.runtime = boot.runtime
        self.market_data = MarketDataStore()

        # generic per-target throttling
        self._last_custom_save_times: dict[str, float] = {}


    def _should_run_save(self, key: str, min_interval_sec: int, force: bool) -> bool:
        if force:
            self._last_custom_save_times[key] = time.time()
            return True

        now = time.time()
        last = self._last_custom_save_times.get(key)
        if last is None or (now - last) >= min_interval_sec:
            self._last_custom_save_times[key] = now
            return True
        return False

    async def save_all_all(self, ib, force=False):

        # self.runtime.save_application_state()
        FileManager.save_named_json(self.application_state, "application_state")

        ib_dir = self.boot.dirs.ib_dir
        ib_interval = self.app_config.get('intervals',{}).get('ib_posttrade', 300)
        if self._should_run_save("ib_posttrade", ib_interval, force=force):
            # one place where ib_posttrade is called
            logger.info("[save_all_dataframes] Saving IB dataframes ...")
            await ib_posttrade.save_ib_dfs_async(ib_dir, ib)

        self.logger.info(f"[save_all_dataframes] Completed save (force={force})")


    # --------------------------
    # BELOW ARE YOUR LOOP HANDLERS
    # --------------------------

    async def engine_loop(self, ib):
        run_number = 0
        initial_setup = False
        custom_option_data = {}
        while True:
            try:
                start_time = time.time()
                run_number += 1
                current_hh_mm_ny = self.runtime.now_hhmm()
                current_date_time_ny = self.runtime.now_Y_M_D_H_S()
                unique_run_number =  self.runtime.generate_unique_run_number(run_number)
                self.app_config = self.runtime.reload_config()
                self.application_statep['current_date_time_ny'] = current_date_time_ny
                self.application_statep['unique_run_number'] = unique_run_number

                logger.warning(f"==================== unique_run_number: {unique_run_number}, current_hh_mm_ny: {current_hh_mm_ny}")
                if ib is None:
                    logger.warning("ib is None... so gie a try to reconnect ...")
                    await asyncio.sleep(3)
                    continue

                symbol_price = self.application_state.get('symbols', {}).get('SPX', {}).get('current_price', None)
                logger.info(f"symbol_price: {symbol_price} ")
                if symbol_price is None or symbol_price == -1 or np.isnan(symbol_price):
                    logger.info(f"@@ Waiting for valid SPX price...symbol_price: {symbol_price}")
                    await asyncio.sleep(1)
                    continue
                atm_strike = options_helper.get_atm_strike_price(symbol_price)
                self.application_state.setdefault('symbols', {}).setdefault('SPX', {})['atm_strike'] = atm_strike
                logger.info(f"@@ atm_strike: {atm_strike} for symbol_price: {symbol_price}")
                if not initial_setup:
                    initial_setup = True
                    # initial tasks can be placed here
                bid_ask_for_c_and_p_map = await options_helper.get_spx_option_chain_bid_ask(ib, atm_strike, self.app_config, self.application_state)
                options_helper.calualte_misc_metrics(custom_option_data, self.app_config, self.application_state)
                custom_option_data_map = options_helper.convert_to_map_ready_for_stream(custom_option_data, self.app_config, self.application_state)



                self.application_state.setdefault('symbols', {}).setdefault('SPX', {})['option_chain'] = bid_ask_for_c_and_p_map
                custom_option_data.append(bid_ask_for_c_and_p_map)


                end_time = time.time()
                run_spend_time = round(end_time - start_time, 2)
                logger.warning(f'==================== unique_run_number: {unique_run_number}, run_spent_time: {run_spend_time} seconds, no sleep ...')

                await asyncio.sleep(self.app_config['interval_seconds']['engine_loop'])
            except Exception as e:
                logger.warning(f"@@@ Unexpected error in engine_loop: {e}")
                logger.error(f"@@@ error: {traceback.format_exc()}" )
                await asyncio.sleep(self.app_config['interval_seconds']['engine_loop'])

    async def spx_price_stream_loop(self, ib):
        global spx_current_price

        spx_current_price = await ib_pricing_async.subscribe_symbol_once(ib, "SPX", secType="IND", exchange="CBOE")

        while True:
            try:
                spx_current_price = ib_pricing_async.get_latest_price('SPX')
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
                await asyncio.sleep(0.1)
                logger.info(f"spx_price_stream_loop in the streem loop  spx_current_price: {spx_current_price} ")
            except Exception as e:
                logger.warning(f"Unexpected error in spx_price_stream_loop: {e}")

    async def test_loop(self, ib):
        while True:
            try:
                logger.info("test_loop...")
                await asyncio.sleep(10)
            except Exception as e:
                logger.warning(f"Unexpected error: {e}")
                logger.error(f"@@@ error: {traceback.format_exc()}" )

    async def request_router(self):
        while True:
            try:
                user_request_fetcher.fetch_user_request(self.app_config, self.application_state)
                logger.info("request_router...")
                await asyncio.sleep(10)
            except Exception as e:
                logger.warning(f"Unexpected error: {e}")
                logger.error(f"@@@ error: {traceback.format_exc()}" )

    async def data_saver_loop(self, ib):
        while True:
            try:

                if self.application_state.get('is_busy_time', False):
                    self.logger.info("[data_saver] Busy hour -> skip save")
                    await asyncio.sleep(30)
                    continue

                await self.save_all_all(ib, force=False)

                await asyncio.sleep(60)

            except Exception as e:
                self.logger.error(f"@@@ [data_saver] Error: {e}")
                await asyncio.sleep(10)

    async def run(self):
        logger.info("Starting Trading Engine")
        ib = await IBConnector.connect_from_config(self.app_config)

        ws_server = await self.ws.start()

        state_streamer = StateStreamer(self.application_state, self.ws, interval=5)
        config_streamer = ConfigStreamer(self.app_config, self.ws, interval=12)

        self.logger.info("WebSocket server is starting...")

        await asyncio.gather(
            ws_server,
            state_streamer.run(),
            config_streamer.run(),
            self.engine_loop(ib),
            self.test_loop(ib),
            self.request_router(),
            self.data_saver_loop(ib)
        )