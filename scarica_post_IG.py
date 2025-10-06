#Tutte le foto e i video verranno salvati in una cartella con il nome del profilo, già organizzate per data e tipo.
import instaloader

# Crea una istanza
L = instaloader.Instaloader()

# Login (credenziali Instagram)
USERNAME = 'tuo_username_instagram'
PASSWORD = 'tua_password_instagram'
L.login(USERNAME, PASSWORD)  # Puoi omettere questa riga se il profilo è pubblico

# Scarica tutti i post del tuo profilo
profile = instaloader.Profile.from_username(L.context, USERNAME)
for post in profile.get_posts():
    L.download_post(post, target=USERNAME)
