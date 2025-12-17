
from PIL import Image
import os

def resize_folder(input_folder, output_folder, size=(640, 480)):
    for filename in os.listdir(input_folder):
        if filename.endswith('.jpg'):
            img = Image.open(os.path.join(input_folder, filename))
            img = img.resize(size)
  
img.save(os.path.join(output_folder, filename))

