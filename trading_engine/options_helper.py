
import logging
logger = logging.getLogger(__name__)
from trading_utils import ib_contract

def get_atm_strike_price(application_state, symbol, symbol_price):
    atm = round(symbol_price / 5) * 5
    application_state['symbols'][symbol]['atm_strike'] = atm
    logger.info(f"Calculated ATM strike for {symbol}: {atm} based on price {symbol_price}")
    return atm

async def  create_spx_option_contract(ib, app_config, application_state, symbol, expiry, strike, right):
    from trading_utils import ib_contract
    qc = await ib_contract.get_option_contract_cached(ib,symbol, expiry, strike, right)

    return qc



# def get_closest_expiry_and_atm_strike():# --- Step 1: Define SPX underlying ---
#     underlying = Index('SPX', 'CBOE')  # SPX is the underlying for SPXW
#     ib.qualifyContracts(underlying)
#
#     # --- Step 2: Request option chain info ---
#     chains = ib.reqSecDefOptParams('SPX', '', 'IND', underlying.conId)
#
#     # SPXW is a weekly trading class for SPX index options
#     chain = next(c for c in chains if c.tradingClass == 'SPXW')
#
#     # --- Step 3: Get current SPX price ---
#     ticker = ib.reqMktData(underlying)
#     ib.sleep(2)
#     underlying_price = ticker.last or ticker.close
#     logger.info(f"SPX current price: {underlying_price}")
#
#     # --- Step 4: Choose expiry ---
#     expiry = sorted(chain.expirations)[0]   # nearest expiry
#     logger.info(f"Nearest expiry: {expiry}")
#
#     # --- Step 5: Find ATM strike ---
#     strikes = sorted(chain.strikes)
#     atm_strike = min(strikes, key=lambda s: abs(s - underlying_price))
#
#     logger.info(f"ATM Strike: {atm_strike}")
#     return expiry, atm_strike
