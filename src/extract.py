import requests
import json


base = 'https://api.coingecko.com/api/v3'

# url = '/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1' # 1

# url = '/coins/list' # dim_coin

url = ''

response = requests.get(f"{base}{url}")

data = response.json()

print(json.dumps(data, indent=4, ensure_ascii=False))

# with open("resultado.json", 'w') as f:
#     json.dump(data, f, indent=4, ensure_ascii=False)
