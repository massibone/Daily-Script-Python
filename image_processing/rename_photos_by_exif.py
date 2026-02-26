Rinomina e organizza automaticamente i file fotografici basandosi sui metadati EXIF.

Formato output personalizzabile, es: YYYY-MM-DD_Citta_001.jpg

Caratteristiche:
- Estrazione data/ora di scatto dai dati EXIF.
- Fallback alla data di modifica del file se i dati EXIF sono assenti.
- Geocodifica inversa (opzionale) per ottenere la città dalle coordinate GPS.
- Cache per le richieste di geocodifica per ridurre le chiamate API e accelerare il processo.
- Supporto per formati HEIC/HEIF (richiede `pillow-heif`).
- Gestione robusta dei conflitti di nome file.
- Modalità copia o sposta.
- Formato del nome file personalizzabile.
- Barra di progresso per un feedback visivo durante l'elaborazione.
- Gestione delle dipendenze mancanti con richiesta di installazione.

Usage:
    python rename_photos_by_exif.py <input_folder> <output_folder> [options]

Esempi:
  # Copia le foto con rinomina base
  python rename_photos_by_exif.py ./foto_input ./foto_output

  # Sposta le foto e abilita la ricerca della città tramite GPS
  python rename_photos_by_exif.py ./foto_input ./foto_output --move --enable-gps

  # Usa un formato di nome file personalizzato
  python rename_photos_by_exif.py ./foto_input ./foto_output --format "{date}_{original_name}_{counter}"
"""

import os
import sys
import shutil
import argparse
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime

# --- Gestione Dipendenze ---
try:
    from PIL import Image, UnidentifiedImageError
    from PIL.ExifTags import TAGS, GPSTAGS
except ImportError:
    print("La libreria 'Pillow' non è installata. Esegui: pip install Pillow")
    sys.exit(1)

try:
    from tqdm import tqdm
except ImportError:
    print("La libreria 'tqdm' non è installata. Esegui: pip install tqdm")
    sys.exit(1)

# --- Configurazione Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    stream=sys.stdout
)

# --- Funzioni di Supporto per Dipendenze ---
def check_and_install_package(package_name, import_name=None):
    import_name = import_name or package_name
    try:
        __import__(import_name)
        if import_name == 'Pillow_Heif':
            from Pillow_Heif import register_heif_opener
            register_heif_opener()
            logging.info("Supporto HEIC/HEIF abilitato.")
    except ImportError:
        logging.warning(f"La libreria '{package_name}' non è installata.")
        response = input(f"Vuoi installare '{package_name}' ora? (s/n): ").lower()
        if response == 's':
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
                logging.info(f"'{package_name}' installato con successo.")
                if import_name == 'Pillow_Heif':
                    from Pillow_Heif import register_heif_opener
                    register_heif_opener()
                    logging.info("Supporto HEIC/HEIF abilitato.")
            except Exception as e:
                logging.error(f"Errore durante l'installazione di '{package_name}': {e}")
                sys.exit(1)
        else:
            logging.warning(f"Funzionalità dipendenti da '{package_name}' non saranno disponibili.")

class PhotoRenamer:
    """Classe per rinominare e organizzare foto basandosi su dati EXIF."""

    SUPPORTED_FORMATS = ('.jpg', '.jpeg', '.png', '.tiff', '.tif', '.heic', '.heif')

    def __init__(self, input_dir, output_dir, enable_gps=False, copy_mode=True, filename_format="{date}_{city}_{counter}"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.enable_gps = enable_gps
        self.copy_mode = copy_mode
        self.filename_format = filename_format
        self.processed = 0
        self.failed = 0
        self.cache_file = self.output_dir / ".geocoding_cache.json"
        self.geocoding_cache = self._load_cache()

        if not self.input_dir.is_dir():
            raise FileNotFoundError(f"Cartella input non trovata o non valida: {input_dir}")

        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _load_cache(self):
        if self.cache_file.exists():
            try:
                with self.cache_file.open('r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logging.warning(f"Impossibile caricare la cache di geocoding: {e}")
        return {}

    def _save_cache(self):
        try:
            with self.cache_file.open('w', encoding='utf-8') as f:
                json.dump(self.geocoding_cache, f, indent=4)
        except IOError as e:
            logging.warning(f"Impossibile salvare la cache di geocoding: {e}")

    def get_exif_data(self, image_path):
        try:
            img = Image.open(image_path)
            exif_data = img.getexif()
            if not exif_data:
                return None

            exif = {TAGS.get(tag_id, tag_id): value for tag_id, value in exif_data.items()}
            return exif
        except (IOError, UnidentifiedImageError) as e:
            logging.warning(f"Impossibile leggere il file immagine {image_path.name}: {e}")
            return None
        except Exception as e:
            logging.warning(f"Errore imprevisto durante la lettura EXIF di {image_path.name}: {e}")
            return None

    def get_date_taken(self, exif_data):
        if not exif_data:
            return None
        date_tags = ['DateTimeOriginal', 'DateTime', 'DateTimeDigitized']
        for tag in date_tags:
            if tag in exif_data:
                try:
                    date_str = str(exif_data[tag])
                    return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
                except (ValueError, TypeError):
                    continue
        return None

    def _convert_to_degrees(self, value):
        if not value or len(value) < 3:
            return None
        d, m, s = value
        return float(d) + float(m) / 60 + float(s) / 3600

    def get_gps_coordinates(self, exif_data):
        if not exif_data or not self.enable_gps or 'GPSInfo' not in exif_data:
            return None, None

        try:
            gps_info = {GPSTAGS.get(key, key): value for key, value in exif_data['GPSInfo'].items()}
            lat = self._convert_to_degrees(gps_info.get('GPSLatitude'))
            lon = self._convert_to_degrees(gps_info.get('GPSLongitude'))

            if lat is None or lon is None:
                return None, None

            if gps_info.get('GPSLatitudeRef') == 'S': lat = -lat
            if gps_info.get('GPSLongitudeRef') == 'W': lon = -lon

            return lat, lon
        except (TypeError, IndexError, KeyError, AttributeError) as e:
            logging.warning(f"Errore durante il parsing delle coordinate GPS: {e}")
            return None, None

    def get_city_from_gps(self, lat, lon):
        if not lat or not lon:
            return ""

        cache_key = f"{lat:.4f},{lon:.4f}"
        if cache_key in self.geocoding_cache:
            return self.geocoding_cache[cache_key]

        try:
            import requests
            url = "https://nominatim.openstreetmap.org/reverse"
            params = {'lat': lat, 'lon': lon, 'format': 'json', 'zoom': 10}
            headers = {'User-Agent': 'PhotoRenamer/2.0'}

            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            address = data.get('address', {})

            city = (address.get('city') or address.get('town') or address.get('village') or address.get('municipality') or '')
            city_clean = city.replace(' ', '_').replace('/', '-')
            city_clean = city_clean[:30]

            self.geocoding_cache[cache_key] = city_clean
            return city_clean

        except ImportError:
            logging.error("'requests' non è installato. Impossibile ottenere la città.")
            self.enable_gps = False # Disabilita per le prossime chiamate
            return ""
        except requests.exceptions.RequestException as e:
            logging.error(f"Errore di rete durante il geocoding: {e}")
            return ""
        except Exception as e:
            logging.error(f"Errore imprevisto durante il geocoding: {e}")
            return ""

    def generate_new_filename(self, image_path, counter):
        exif_data = self.get_exif_data(image_path)

        date = self.get_date_taken(exif_data)
        date_str = date.strftime("%Y-%m-%d") if date else datetime.fromtimestamp(image_path.stat().st_mtime).strftime("%Y-%m-%d")

        city = ""
        if self.enable_gps:
            lat, lon = self.get_gps_coordinates(exif_data)
            if lat and lon:
                city = self.get_city_from_gps(lat, lon)

        format_data = {
            "date": date_str,
            "city": city,
            "counter": f"{counter:03d}",
            "original_name": image_path.stem,
        }

        try:
            new_name_base = self.filename_format.format(**format_data)
        except KeyError as e:
            logging.warning(f"Variabile non valida '{e}' nel formato. Uso il formato di default.")
            self.filename_format = "{date}_{city}_{counter}"
            new_name_base = self.filename_format.format(**format_data)

        new_name_base = new_name_base.replace('__', '_').strip('_')
        return f"{new_name_base}{image_path.suffix.lower()}"

    def process_photo(self, image_path, counter):
        try:
            new_name = self.generate_new_filename(image_path, counter)
            new_path = self.output_dir / new_name

            i = 1
            while new_path.exists():
                new_path = self.output_dir / f"{new_path.stem}_dup{i}{new_path.suffix}"
                i += 1

            action = "Copiato" if self.copy_mode else "Spostato"
            if self.copy_mode:
                shutil.copy2(image_path, new_path)
            else:
                shutil.move(str(image_path), str(new_path))

            logging.info(f"{action}: {image_path.name} -> {new_path.name}")
            self.processed += 1
            return True

        except Exception as e:
            logging.error(f"Fallito processo per {image_path.name}: {e}")
            self.failed += 1
            return False

    def run(self):
        print(f"\n{'='*60}")
        print(f"📸 PHOTO RENAMER BY EXIF v2.0")
        print(f"{'='*60}")
        print(f"Input:  {self.input_dir}")
        print(f"Output: {self.output_dir}")
        print(f"GPS:    {'Abilitato' if self.enable_gps else 'Disabilitato'}")
        print(f"Modo:   {'Copia' if self.copy_mode else 'Sposta'}")
        print(f"Formato: {self.filename_format}")
        print(f"{'='*60}\n")

        photos = []
        for ext in self.SUPPORTED_FORMATS:
            photos.extend(self.input_dir.rglob(f"*{ext}"))
            photos.extend(self.input_dir.rglob(f"*{ext.upper()}"))
        
        photos = sorted(list(set(photos)), key=lambda p: p.stat().st_mtime)

        if not photos:
            logging.warning("Nessuna foto trovata nella cartella input.")
            return

        logging.info(f"Trovate {len(photos)} foto da processare...\n")

        for i, photo in enumerate(tqdm(photos, desc="Processando foto", unit="file"), 1):
            self.process_photo(photo, i)

        self._save_cache()

        print(f"\n{'='*60}")
        print("Riepilogo:")
        print(f"  ✓ Processate con successo: {self.processed}")
        print(f"  ✗ Fallite:               {self.failed}")
        print(f"{'='*60}\n")

def main():
    parser = argparse.ArgumentParser(
        description="Rinomina e organizza foto in base ai dati EXIF (data, città, sequenza).",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Esempi d'uso:
  python rename_photos_by_exif.py ./foto ./rinominate
  python rename_photos_by_exif.py ./foto ./spostate --move --enable-gps
  python rename_photos_by_exif.py ./foto ./custom --format "{date}_{original_name}"

Formati supportati: JPG, JPEG, PNG, TIFF, TIF, HEIC, HEIF
(HEIC/HEIF richiedono 'pillow-heif')

Variabili per --format:
  {date}          - Data nel formato YYYY-MM-DD
  {city}          - Città estratta dal GPS (se abilitato)
  {counter}       - Contatore sequenziale (es. 001)
  {original_name} - Nome del file originale senza estensione
"""
    )

    parser.add_argument("input_dir", help="Cartella contenente le foto da processare.")
    parser.add_argument("output_dir", help="Cartella di destinazione per le foto processate.")
    parser.add_argument("--enable-gps", action="store_true", help="Abilita la ricerca della città tramite GPS (richiede 'requests').")
    parser.add_argument("--move", action="store_true", help="Sposta i file invece di copiarli.")
    parser.add_argument("--format", default="{date}_{city}_{counter}", help="Formato personalizzato per il nome del file.")

    args = parser.parse_args()

    if args.enable_gps:
        check_and_install_package('requests')
    
    # Controlla sempre per il supporto HEIC/HEIF
    check_and_install_package('pillow-heif', 'Pillow_Heif')

    try:
        renamer = PhotoRenamer(
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            enable_gps=args.enable_gps,
            copy_mode=not args.move,
            filename_format=args.format
        )
        renamer.run()
    except FileNotFoundError as e:
        logging.error(e)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nOperazione interrotta dall'utente.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Si è verificato un errore imprevisto: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
