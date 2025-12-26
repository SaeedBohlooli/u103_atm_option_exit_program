import requests
print('# ###########################')

host= '127.0.0.1'
port = 5103

def get_setup_order():
    d = {'api_request_id': '20251225-204024',
         'atm_trigger': '',
         'base_atm_trigger': '',
         'frequency': '',
         'request_type': 'SETUP_ORDER',
         'rolling_number': '',
         'spx_price_trigger': '',
         'orders': [{'base_atm_price': '',
                     'close_long_strike': '',
                     'close_long_strike_combo': '',
                     'close_long_strike_single_leg': '',
                     'close_short_strike': '',
                     'close_short_strike_combo': '',
                     'contracts': '',
                     'entry_spx_price': '',
                     'limit_order_type_limit': '',
                     'option_type': ''},
                    {'base_atm_price': '',
                     'close_long_strike': '',
                     'close_long_strike_combo': '',
                     'close_long_strike_single_leg': '',
                     'close_short_strike': '',
                     'close_short_strike_combo': '',
                     'contracts': '',
                     'entry_spx_price': '',
                     'limit_order_type_limit': '',
                     'option_type': ''}],
         'status': 'WEB_SUBMITTED'}
    return d , "api/send_request" , "post"


d , u , m = get_setup_order()

url = f"http://{host}:{port}/{u}"
print(f"Sending request to {url}")
if  m == "post":
    resp = requests.post(
        url, json=d
    )
else:
    resp = requests.get(
        url
    )

print(d)
print(f"url:{url}")
print(f"Status:{resp.status_code}")
print(f"rest:{resp}")
print(f"Response:{resp.json()}")

print('# ###########################')
print('# ###########################')



if True:

    url = f"http://{host}:{port}/api/health"
    print(f"Checking health at {url}")
    resp = requests.get(url)

    print("Status:", resp.status_code)
    print("Body:", resp.json())


    print('# ###########################')
    print('# ###########################')
