# save_instagram_posts.py

# Importiamo la libreria instaloader, il nostro "coltellino svizzero" per Instagram.
import instaloader

# Creiamo un'istanza della classe Instaloader.
L = instaloader.Instaloader()

# La funzione input() mette in pausa lo script e attende un inserimento da tastiera.
post_url = input("Inserisci l'URL del post di Instagram da salvare: ")

# Esempio: da "https://www.instagram.com/p/CqZ_j.../" estraiamo "CqZ_j...".
# Usiamo il metodo split( ) per "rompere" la stringa dell'URL dove c'è "/p/"
# e poi di nuovo al "/" successivo per isolare lo shortcode.
try:
    shortcode = post_url.split("/p/")[1].split("/")[0]
except IndexError:
    print("URL non valido. Assicurati di inserire un URL di un post valido.")
    exit()

print(f"Sto scaricando il post con shortcode: {shortcode}")

try:
    #    L.context contiene le informazioni di sessione.
    post = instaloader.Post.from_shortcode(L.context, shortcode)

    
    #    In questo caso, la cartella avrà il nome dello shortcode.
    L.download_post(post, target=shortcode)

    print(f"Download completato! Il post è stato salvato nella cartella '{shortcode}'.")

except Exception as e:
    print(f"Si è verificato un errore durante il download: {e}")
    print("Potrebbe essere necessario effettuare il login per post privati o per limiti di richieste.")


