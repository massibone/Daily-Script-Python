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
