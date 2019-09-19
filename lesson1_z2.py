import requests
from pprint import pprint
import json


user_ids = '21915'
access_token = '4e1ee1e44e1ee1e44e1ee1e4284e7273df44e1e4e1ee1e413788812bb6076470f859b65'
repos = requests.get(f'https://api.vk.com/method/users.get?user_ids={user_ids}&fields=bdate&access_token={access_token}'
                     f'&v=5.101')
pprint(repos)
data = json.loads(repos.text)

with open('response_lesson1_z2.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, indent=2, ensure_ascii=False)
