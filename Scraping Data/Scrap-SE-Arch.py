import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()
api_key=os.getenv("Stack_Api")
base_url = f"https://api.stackexchange.com/2.3/questions?key={api_key}"
params = {
    'tagged': 'arch-linux', 
    'answers': 'true',
    'order': 'desc',
    'sort': 'votes',
    'site': 'unix',
    'filter':'!*Mg4PjfftzEy7OEn'
    
}

all_items = []
page = 1
total_pages_to_fetch = 167

while len(all_items) < 5000 and page <= total_pages_to_fetch:
    params['page'] = page
    response = requests.get(base_url, params=params)
    data = response.json()
    
    if 'items' in data:
        all_items.extend(data['items'])
    else:
        break
        
    if not data.get('has_more'):
        break
        
    page += 1



print(f"Retrieved {len(all_items)} items.")
fileName = "Finetuning-Qwen-Lora"
subDir="Scraping Data"
jsonName= "arch_questions.json"
path = os.path.join(fileName,subDir,jsonName)
with open(path, 'w', encoding='utf-8') as f:
    json.dump(all_items, f, indent=4)