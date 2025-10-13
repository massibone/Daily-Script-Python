# Estrazione immagini da Instagram
import instaloader
def download_images(profile):
    loader = instaloader.Instaloader()
    for post in instaloader.Profile.from_username(loader.context, profile).get_posts():
        loader.download_post(post, target=profile)
