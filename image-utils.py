#image-utils.py
import os
from PIL import Image

def resize_image(image_path, output_path, size):
"""
Ridimensiona un'immagine.

Args:
image_path (str): Percorso dell'immagine di input.
output_path (str): Percorso dell'immagine di output.
size (tuple): Dimensioni dell'immagine di output (larghezza, altezza).

Returns:
None
"""
img = Image.open(image_path)
img = img.resize(size)
img.save(output_path)

def rotate_image(image_path, output_path, angle):
"""
Ruota un'immagine.

Args:
image_path (str): Percorso dell'immagine di input.
output_path (str): Percorso dell'immagine di output.
angle (int): Angolo di rotazione.
Returns:
None
"""
img = Image.open(image_path)
img = img.rotate(angle)
img.save(output_path)

def convert_image_format(image_path, output_path, format):
"""
Converte il formato di un'immagine.

Args:
image_path (str): Percorso dell'immagine di input.
output_path (str): Percorso dell'immagine di output.
format (str): Formato di output (ad esempio "jpg", "png", ecc.).

Returns:
None
"""
img = Image.open(image_path)
img.save(output_path, format)

def main():
# Esempio di utilizzo
image_path = "input.jpg"
output_path = "output.jpg"

# Ridimensiona l'immagine
resize_image(image_path, output_path, (800, 600))

# Ruota l'immagine
rotate_image(image_path, output_path, 45)

# Converte il formato dell'immagine
convert_image_format(image_path, output_path, "png")

if __name__ == "__main__":
main()
