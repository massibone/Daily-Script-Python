#esegue un'operazione di crop facile per Instagram 
from PIL import Image

def auto_crop(image, ratio):
"""
Esegue un'operazione di crop facile per Instagram.

Args:
image (Image): Immagine da cropare.
ratio (float): Rapporto di aspetto per il crop (ad esempio 1.91 per Instagram).

Returns:
Image: Immagine cropata.
"""
# Ottieni le dimensioni dell'immagine
width, height = image.size
