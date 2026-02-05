import os
import requests

def upload_image(image_path, upload_url):
    """
    Carica un'immagine sul server.

    :param image_path: Percorso dell'immagine da caricare
    :param upload_url: URL del server per il caricamento
    """
    with open(image_path, 'rb') as image_file:
        files = {'file': image_file}
        response = requests.post(upload_url, files=files)
        return response


def upload_images_from_folder(folder_path, upload_url):
    """
    Carica tutte le immagini da una cartella.

    :param folder_path: Percorso della cartella contenente le immagini
    :param upload_url: URL del server per il caricamento
    """
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            image_path = os.path.join(folder_path, filename)
            response = upload_image(image_path, upload_url)
            print(f"Caricamento di {filename}: {response.status_code} - {response.text}")


if __name__ == "__main__":
    folder_path = 'percorso/della/tua/cartella'  # Sostituisci con il percorso della tua cartella
    upload_url = 'https://tuo-server.com/upload'  # Sostituisci con l'URL per il caricamento
    upload_images_from_folder(folder_path, upload_url)



