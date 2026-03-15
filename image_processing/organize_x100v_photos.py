organize_x100v_photos.py
import os
import shutil
from datetime import datetime
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def get_exif_data(image_path):
    """Estrae i dati EXIF da un'immagine."""
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        if not exif_data:
            return {}
        exif = {}
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            exif[tag] = value
        return exif
    except Exception as e:
        print(f"Errore nel leggere EXIF da {image_path}: {e}")
        return {}

def get_date_taken(exif):
    """Estrae la data di scatto dal campo EXIF DateTimeOriginal."""
    date_str = exif.get('DateTimeOriginal') or exif.get('DateTime')
    if date_str:
        try:
            return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
        except ValueError:
            pass
    return None

def get_focal_length(exif):
    """Estrae la lunghezza focale dal campo EXIF FocalLength."""
    focal = exif.get('FocalLength')
    if focal:
        if isinstance(focal, tuple) and len(focal) == 2 and focal[1] != 0:
            return round(focal[0] / focal[1])
        elif isinstance(focal, (int, float)):
            return int(focal)
    return None

def organize_photos(source_folder):
    """Organizza i file RAF rinominandoli e spostandoli in cartelle anno/mese."""
    source = Path(source_folder)
    if not source.exists():
        print(f"Cartella {source_folder} non trovata.")
        return

    for file_path in source.glob('*.RAF'):
        exif = get_exif_data(file_path)
        date_taken = get_date_taken(exif)
        focal_length = get_focal_length(exif)

        if not date_taken:
            print(f"Data EXIF non trovata per {file_path.name}, salto file.")
            continue

        # Costruisci nome file: YYYY-MM-DD_locazione_focale.RAF
        # Qui 'locazione' è un placeholder, puoi modificarlo o estrarlo da EXIF GPS se vuoi
        location = "locazione"  # Puoi implementare estrazione GPS se necessario
        focal_str = f"{focal_length}mm" if focal_length else "nofocal"
        new_filename = f"{date_taken.strftime('%Y-%m-%d')}_{location}_{focal_str}.RAF"

        # Cartella destinazione anno/mese
        dest_folder = source / str(date_taken.year) / f"{date_taken.month:02d}"
        dest_folder.mkdir(parents=True, exist_ok=True)

        dest_path = dest_folder / new_filename

        # Evita sovrascrittura rinominando se necessario
        counter = 1
        while dest_path.exists():
            dest_path = dest_folder / f"{date_taken.strftime('%Y-%m-%d')}_{location}_{focal_str}_{counter}.RAF"
            counter += 1

        # Sposta e rinomina il file
        shutil.move(str(file_path), str(dest_path))
        print(f"Spostato {file_path.name} → {dest_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Uso: python organize_x100v_photos.py <cartella_foto>")
    else:
        organize_photos(sys.argv[1])
      
