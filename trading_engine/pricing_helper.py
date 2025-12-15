import logging
logger = logging.getLogger(__name__)
from trading_utils import ib_contract
from trading_utils import ib_pricing_async

async def get_bid_ask_for_contracts(ib, app_config, application_state, contracts):
    logger.info(f'Getting bid and ask for contracts...{contracts}')
    await ib_pricing_async.subscribe_contracts_to_market_data(ib, contracts)
    quotes_df = ib_pricing_async.get_all_quotes_as_df()
    logger.info(f"get_bid_ask_for_contracts, quotes_df: \n{quotes_df.to_markdown()} ")
    return quotes_df

