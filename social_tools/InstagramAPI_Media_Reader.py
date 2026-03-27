# MiniScript: Instagram API Media Reader
#Questo mini script Python permette di visualizzare gli ultimi post pubblicati da un account Instagram Business o Creator collegato a una pagina Facebook, usando la Graph API ufficiale.

## Come funziona

#1. Copia il tuo Access Token di Instagram Graph API e il tuo user_id.
#2. Inseriscili nel file `miniscript.py`.
#3. Avvia lo script con:
    ```
    python miniscript.py
    ```
#4. Visualizzerai a terminale ID, caption, URL, data e permalink dei tuoi post.

## Requisiti
'''
- Python ≥ 3.9
- Libreria `requests` (`pip install requests`)

## Note
- Necessario account Instagram Business/Creator collegato a Facebook.
- Access Token valido tramite Facebook Developer Console.
'''
import requests

access_token = 'IL_TUO_ACCESS_TOKEN'  # Inserisci qui il tuo access token
user_id = 'ID_UTENTE_INSTAGRAM'       # Scopri il tuo user id dal Graph API Explorer

endpoint = f"https://graph.instagram.com/{user_id}/media"
params = {
    'fields': 'id,caption,media_type,media_url,permalink,timestamp',
    'access_token': access_token
}

response = requests.get(endpoint, params=params)
if response.status_code == 200:
    data = response.json().get('data', [])
    for post in data:
        print(f"ID: {post['id']}")
        print(f"Caption: {post.get('caption', '')}")
        print(f"URL: {post['media_url']}")
        print(f"Data: {post['timestamp']}")
        print(f"Permalink: {post['permalink']}")
        print("-" * 40)
else:
    print("Errore:", response.status_code, response.text)
