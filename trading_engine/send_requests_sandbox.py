import random

import requests
print('# ###########################')

host= '127.0.0.1'
port = 5103

import random


def get_setup_order():
    x = random.randint(1,1000)
    d = {
        'web_request_id': f'20260102-124150-1-{x}',
        'status': 'WEB_SUBMITTED',
         'request_type': 'SETUP_ORDER',
         'rolling_number': '',
         'atm_trigger': -1, #a
         'spx_price_trigger': 1, #b
         'base_atm_trigger': 5, #c
         'frequency': '',
         'orders': [{
                     'entry_spx_price': 6880, #d
                     'base_atm_price': 6850, #e
                     'contracts': 1, #f
                     'option_right': 'C', #g
                     'close_short_strike': 0, #h
                     'close_long_strike': 6850, #i
                     'cancel_short_strike_combo': 0, #k
                     'cancel_long_strike_combo': 0,  #l
                     'cancel_long_strike_single_leg': 0,  #m
                     'cancel_short_strike_single_leg': 0,  #n
                     'limit_order_type_limit': '', # j
                    }
]

    }
    return d , "api/send-request" , "post"


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
