from PIL import Image
import os

def crea_thumbnail(input_path, output_path, size=(300, 300)):
    """
    Crea una thumbnail da un'immagine, mantenendo le proporzioni originali.
    Args:
        input_path (str): Percorso dell'immagine di input.
        output_path (str): Percorso dove salvare la thumbnail.
        size (tuple): Dimensione massima della thumbnail (larghezza, altezza).
    """
    try:
        with Image.open(input_path) as img:
            # Mantieni le proporzioni
            img.thumbnail(size)

            # Assicurati che la directory di output esista
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Salva la thumbnail
            img.save(output_path)
            print(f"Thumbnail salvata con successo in: {output_path}")
    except Exception as e:
        print(f"Errore durante la creazione della thumbnail: {e}")

# Esempio di utilizzo:
# crea_thumbnail("percorso/immagine_originale.jpg", "percorso/thumbnail.jpg")
