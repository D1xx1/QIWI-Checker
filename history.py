'''Данный модуль писался для проверки QIWI API.
Он никак не используется при работе бота.'''

import requests
import json
import settings

def story():
    api_access_token = settings.qiwi_token
    my_login = settings.qiwi_number
    s = requests.Session()
    s.headers['authorization'] = 'Bearer ' + api_access_token  
    parameters = {'rows': '20'}
    h = s.get('https://edge.qiwi.com/payment-history/v1/persons/'+my_login+'/payments', params = parameters)
    hist = json.loads(h.text)
    for i in range(20):
        if hist['data'][i]['comment'] is not None:
            print(hist['data'][i]['comment'])
            print(hist['data'][i]['sum']['amount'])


story()