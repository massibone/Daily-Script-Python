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

# Calcola le nuove dimensioni per il crop
new_width = int(height * ratio)
new_height = height

# Se la nuova larghezza è maggiore della larghezza originale, usa la larghezza originale
if new_width > width:
new_width = width
new_height = int(width / ratio)

# Calcola le coordinate per il crop
left = (width - new_width) // 2
top = (height - new_height) // 2
right = left + new_width
bottom = top + new_height

# Esegue il crop
cropped_image = image.crop((left, top, right, bottom))

return cropped_image
'''Esempio di utilizzo
from PIL import Image

# Carica l'immagine
image = Image.open("input.jpg")

# Esegue il crop
cropped_image = auto_crop(image, 1.91)

# Salva l'immagine cropata
cropped_image.save("output.jpg")

