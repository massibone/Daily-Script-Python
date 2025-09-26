## Batch Image Renamer (Fuji X100V)
#Script per rinominare in automatico file .jpg generati da Fuji.  
### Uso  
#python renamer.py --path dir  
### Output  
#Rinominazione batch con data + localizzazione.
import os
import argparse
from datetime import datetime
import gps

def renamer(path):
  for root, dirs, files in os.walk(path):
  for file in files:
  if file.endswith(".jpg"):
    # Leggi i metadati dell'immagine
    with open(os.path.join(root, file), 'rb') as f:
    img = gps.GPSPhoto(f)
    # Estrai la data e la localizzazione
    date = img.date
    lat = img.latitude
    lon = img.longitude
    # Rinomina il file
    new_name = f"{date}_{lat}_{lon}.jpg"
    os.rename(os.path.join(root, file), os.path.join(root, new_name))
    print(f"Rinominato: {file} -> {new_name}")

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Batch Image Renamer")
  parser.add_argument("--path", help="Percorso della cartella contenente le immagini", required=True)
  args = parser.parse_args()
  renamer(args.path)
