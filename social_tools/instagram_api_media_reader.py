# Importiamo la classe Client da instagrapi e la libreria getpass per la password.
from instagrapi import Client
import getpass
import json

# Creiamo un'istanza del client API.
cl = Client()

# getpass.getpass nasconde l'input della password per sicurezza.
username = input("Inserisci il tuo nome utente Instagram: ")
password = getpass.getpass("Inserisci la tua password Instagram: ")

print("Accesso in corso...")
try:
    cl.login(username, password)
    print("Accesso effettuato con successo!")
except Exception as e:
    print(f"Errore durante il login: {e}")
    exit()

# Chiediamo l'URL del post da analizzare.
post_url = input("Inserisci l'URL del post di cui leggere i dati: ")

# Leggere i dati via API
print("\nRecupero le informazioni del post tramite API...")
try:
    # 1. Convertiamo l'URL nell'ID primario del media (media_pk).
    #    Questo è l'identificativo che l'API di Instagram usa internamente.
    media_pk = cl.media_pk_from_url(post_url)

    # 2. Usiamo l'ID per richiedere tutte le informazioni del media.
    #    Questa funzione fa una chiamata all'API privata di Instagram.
    media_info = cl.media_info(media_pk)

    # 3. L'oggetto restituito è complesso. Convertiamolo in un dizionario
    #    per poterlo esplorare e stampare più facilmente.
    media_info_dict = media_info.dict()

    # Lezione 5: Presentare i risultati
    # Stampiamo alcune delle informazioni più interessanti.
    print("\n--- Informazioni Principali del Post ---")
    print(f"ID del Post (PK): {media_info_dict.get('pk')}")
    print(f"Autore: @{media_info_dict.get('user', {}).get('username')}")
    print(f"Numero di 'Mi Piace': {media_info_dict.get('like_count')}")
    print(f"Numero di Commenti: {media_info_dict.get('comment_count')}")
    print(f"Tipo di Media: {media_info_dict.get('media_type')}") # 1: Foto, 2: Video, 8: Album
    print(f"Data di Pubblicazione (UTC): {media_info_dict.get('taken_at')}")
    
    # La didascalia può essere lunga, stampiamo solo le prime 150 battute.
    caption = media_info_dict.get('caption_text', '')
    print(f"Didascalia: {caption[:150]}...")

    # Se vuoi vedere TUTTI i dati disponibili, puoi stampare l'intero dizionario.
    # Attenzione: l'output sarà molto lungo!
    # print("\n--- Dati API Completi (JSON) ---")
    # print(json.dumps(media_info_dict, indent=4, default=str))

except Exception as e:
    print(f"Si è verificato un errore durante il recupero dei dati: {e}")

finally:
    # È buona norma effettuare il logout alla fine.
    cl.logout()
    print("\nLogout effettuato. Sessione chiusa.")


