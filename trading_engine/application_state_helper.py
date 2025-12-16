

def init_application_state(application_state):

    application_state.setdefault('user_input', {})
    application_state['user_input']['symbol'] = 'SPX'
    application_state['user_input']['exchange'] = 'CBOE'
    application_state['user_input']['trading_class'] = 'SPXW'
    application_state['user_input']['trading_class'] = 'SPXW'
    application_state['subscribed_con_ids'] = []  # need to get new quotes ...
    application_state.setdefault('symbols', {}).setdefault('SPX', {'current_price': None})