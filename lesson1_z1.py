import requests
from pprint import pprint
import json

#Получаем список репозиториев пользователя takem792
username = 'takem792'
repos = requests.get(f'https://api.github.com/users/{username}/repos')
data = json.loads(repos.text)

for repo in data:
    pprint(repo['html_url'])

with open('response_lesson1_z1.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, indent=2, ensure_ascii=False)


