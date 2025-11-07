#!/usr/bin/env python3
"""
Estrae le informazioni EXIF dalle immagini e le salva in formato CSV.
Uso:
    python exif_extractor.py /percorso/immagini -o output.csv
"""

import os
import csv
import sys
import argparse
import logging
from datetime import datetime
from fractions import Fraction
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

logger = logging.getLogger(__name__)


class ExifExtractor:
    def __init__(self, supported_formats=None):
        self.supported_formats = supported_formats or ('.jpg', '.jpeg', '.tiff', '.tif')

    # ---- helper: conversione di valori rationals/tuple/num in float ----
    @staticmethod
    def _to_float(val):
        """Converte IFDRational, tuple (num,den), int, float in float. Ritorna None su errori."""
        try:
            # Pillow IFDRational-like object
            if hasattr(val, 'numerator') and hasattr(val, 'denominator'):
                return float(Fraction(val.numerator, val.denominator))
            # tuple (num, den)
            if isinstance(val, tuple) and len(val) == 2:
                num, den = val
                if den:
                    return float(Fraction(num, den))
                return float(num)
            # già numero
            return float(val)
        except Exception:
            return None

    # ---- estrazione EXIF (uso getexif, non _getexif) ----
    def get_exif_data(self, image_path):
        """Estrae i dati EXIF mappando gli id in nomi, e normalizza la sezione GPS."""
        try:
            with Image.open(image_path) as img:
                exif_raw = img.getexif()
                if not exif_raw:
                    return {}

                exif = {}
                for tag_id, value in exif_raw.items():
                    tag = TAGS.get(tag_id, tag_id)

                    if tag == 'GPSInfo' and isinstance(value, dict):
                        gps = {}
                        for gps_id, gps_val in value.items():
                            subtag = GPSTAGS.get(gps_id, gps_id)
                            gps[subtag] = gps_val
                        exif['GPSInfo'] = gps
                    else:
                        exif[tag] = value

                # Fornisco anche la dimensione immagine se non presente negli EXIF
                if 'ExifImageWidth' not in exif or 'ExifImageHeight' not in exif:
                    try:
                        w, h = img.size
                        exif.setdefault('ExifImageWidth', w)
                        exif.setdefault('ExifImageHeight', h)
                    except Exception:
                        # non critico
                        logger.debug("Impossibile leggere image.size")
                return exif

        except Exception as e:
            logger.error(f"Errore nell'estrazione EXIF da {image_path}: {e}")
            logger.debug("Dettaglio exception:", exc_info=True)
            return {}

    # ---- conversione GPS ----
    def convert_gps_to_decimal(self, gps_coord, gps_ref):
        """Converte coordinate GPS (grado,minuto,secondo) in decimali. Gestisce rationals e tuple."""
        try:
            if not gps_coord or not gps_ref:
                return None

            # gps_coord può essere una sequenza di 3 elementi
            deg = self._to_float(gps_coord[0])
            minute = self._to_float(gps_coord[1])
            second = self._to_float(gps_coord[2])

            if deg is None or minute is None or second is None:
                return None

            dec = deg + (minute / 60.0) + (second / 3600.0)
            if str(gps_ref).upper() in ('S', 'W'):
                dec = -dec
            return round(dec, 6)
        except Exception as e:
            logger.debug(f"convert_gps_to_decimal error: {e}")
            return None

    # ---- decode / normalizzazione campi utili ----
    @staticmethod
    def _format_exposure(exp):
        if exp is None:
            return ''
        try:
            if isinstance(exp, tuple) and len(exp) == 2:
                num, den = exp
                if den:
                    return f"{int(num)}/{int(den)}"
            return str(exp)
        except Exception:
            return str(exp)

    @staticmethod
    def _format_fnumber(fnum):
        if fnum is None or fnum == '':
            return ''
        val = ExifExtractor._to_float(fnum)
        if val is None:
            return str(fnum)
        return f"f/{val:.1f}"

    @staticmethod
    def _format_focal(focal):
        if focal is None or focal == '':
            return ''
        val = ExifExtractor._to_float(focal)
        if val is None:
            return str(focal)
        return f"{val:.1f}mm"

    @staticmethod
    def _format_iso(iso):
        if iso is None:
            return ''
        # ISO può essere una lista/tupla
        try:
            if isinstance(iso, (list, tuple)):
                return str(iso[0]) if iso else ''
            return str(iso)
        except Exception:
            return str(iso)

    @staticmethod
    def _decode_flash(flash):
        try:
            fv = int(flash)
            return 'Yes' if (fv & 1) else 'No'
        except Exception:
            return ''

    @staticmethod
    def _decode_white_balance(wb):
        # 0 = Auto, 1 = Manual (valori comuni)
        try:
            w = int(wb)
            return 'Auto' if w == 0 else 'Manual'
        except Exception:
            return str(wb) if wb != '' else ''

    @staticmethod
    def _format_altitude(alt, alt_ref=None):
        # alt può essere tuple o rationals
        try:
            if alt is None:
                return ''
            if hasattr(alt, 'numerator') and hasattr(alt, 'denominator'):
                a = float(Fraction(alt.numerator, alt.denominator))
            elif isinstance(alt, tuple) and len(alt) == 2:
                num, den = alt
                a = float(Fraction(num, den)) if den else float(num)
            else:
                a = float(alt)
            if alt_ref in (1, '1'):  # se 1 indica sotto il livello del mare
                a = -a
            return f"{a:.2f}m"
        except Exception:
            return ''

    # ---- estrazione dei campi principali per il CSV ----
    def extract_key_info(self, exif_data, filename):
        info = {
            'Filename': filename,
            'DateTime': exif_data.get('DateTime', ''),
            'DateTimeOriginal': exif_data.get('DateTimeOriginal', ''),
            'Make': exif_data.get('Make', ''),
            'Model': exif_data.get('Model', ''),
            'ExposureTime': '',
            'FNumber': '',
            'ISO': '',
            'FocalLength': '',
            'Flash': '',
            'WhiteBalance': '',
            'ImageWidth': exif_data.get('ExifImageWidth', ''),
            'ImageHeight': exif_data.get('ExifImageHeight', ''),
            'Orientation': exif_data.get('Orientation', ''),
            'GPS_Latitude': '',
            'GPS_Longitude': '',
            'GPS_Altitude': '',
            'Software': exif_data.get('Software', '')
        }

        # DateTimeOriginal -> ISO (se possibile)
        dto = exif_data.get('DateTimeOriginal') or exif_data.get('DateTime')
        if dto:
            try:
                dt = datetime.strptime(dto, '%Y:%m:%d %H:%M:%S')
                info['DateTimeOriginal'] = dt.isoformat()
            except Exception:
                info['DateTimeOriginal'] = dto

        # ExposureTime
        if 'ExposureTime' in exif_data:
            info['ExposureTime'] = self._format_exposure(exif_data['ExposureTime'])

        # FNumber
        if 'FNumber' in exif_data:
            info['FNumber'] = self._format_fnumber(exif_data['FNumber'])

        # FocalLength
        if 'FocalLength' in exif_data:
            info['FocalLength'] = self._format_focal(exif_data['FocalLength'])

        # ISO
        if 'ISOSpeedRatings' in exif_data:
            info['ISO'] = self._format_iso(exif_data['ISOSpeedRatings'])
        elif 'PhotographicSensitivity' in exif_data:  # fallback se presente
            info['ISO'] = self._format_iso(exif_data['PhotographicSensitivity'])

        # Flash
        if 'Flash' in exif_data:
            info['Flash'] = self._decode_flash(exif_data['Flash'])

        # WhiteBalance
        if 'WhiteBalance' in exif_data:
            info['WhiteBalance'] = self._decode_white_balance(exif_data['WhiteBalance'])

        # GPS
        gps_info = exif_data.get('GPSInfo') or {}
        if gps_info:
            lat_coord = gps_info.get('GPSLatitude')
            lat_ref = gps_info.get('GPSLatitudeRef')
            lon_coord = gps_info.get('GPSLongitude')
            lon_ref = gps_info.get('GPSLongitudeRef')
            alt = gps_info.get('GPSAltitude')
            alt_ref = gps_info.get('GPSAltitudeRef')

            if lat_coord and lat_ref:
                info['GPS_Latitude'] = self.convert_gps_to_decimal(lat_coord, lat_ref)
            if lon_coord and lon_ref:
                info['GPS_Longitude'] = self.convert_gps_to_decimal(lon_coord, lon_ref)
            if alt is not None:
                info['GPS_Altitude'] = self._format_altitude(alt, alt_ref)

        return info

    # ---- scrittura CSV: un helper per evitare duplicazioni ----
    @staticmethod
    def _write_rows_to_csv(fieldnames, row_iterable, output_csv, append=False):
        mode = 'a' if append else 'w'
        write_header = not append or (append and not os.path.exists(output_csv))
        with open(output_csv, mode, newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if write_header:
                writer.writeheader()
            for row in row_iterable:
                writer.writerow(row)

    # ---- processa una directory senza accumulare lista completa in memoria ----
    def process_directory(self, directory_path, output_csv, append=False):
        if not os.path.exists(directory_path):
            logger.error(f"Directory non trovata: {directory_path}")
            return

        fieldnames = [
            'Filename', 'DateTime', 'DateTimeOriginal', 'Make', 'Model',
            'ExposureTime', 'FNumber', 'ISO', 'FocalLength', 'Flash',
            'WhiteBalance', 'ImageWidth', 'ImageHeight', 'Orientation',
            'GPS_Latitude', 'GPS_Longitude', 'GPS_Altitude', 'Software'
        ]

        def rows():
            count = 0
            for root, _, files in os.walk(directory_path):
                for file in files:
                    if file.lower().endswith(self.supported_formats):
                        count += 1
                        image_path = os.path.join(root, file)
                        logger.info(f"Processando: {os.path.basename(image_path)}")
                        exif = self.get_exif_data(image_path)
                        if exif:
                            yield self.extract_key_info(exif, os.path.basename(image_path))
                        else:
                            empty = {f: '' for f in fieldnames}
                            empty['Filename'] = os.path.basename(image_path)
                            yield empty
            logger.info(f"Processati {count} file (directory: {directory_path})")

        self._write_rows_to_csv(fieldnames, rows(), output_csv, append=append)
        logger.info(f"Dati EXIF estratti e salvati in: {output_csv}")

    # ---- processa un singolo file (riusa helper CSV) ----
    def process_single_file(self, image_path, output_csv, append=False):
        if not os.path.exists(image_path):
            logger.error(f"File non trovato: {image_path}")
            return

        if not image_path.lower().endswith(self.supported_formats):
            logger.error(f"Formato file non supportato: {image_path}")
            return

        fieldnames = [
            'Filename', 'DateTime', 'DateTimeOriginal', 'Make', 'Model',
            'ExposureTime', 'FNumber', 'ISO', 'FocalLength', 'Flash',
            'WhiteBalance', 'ImageWidth', 'ImageHeight', 'Orientation',
            'GPS_Latitude', 'GPS_Longitude', 'GPS_Altitude', 'Software'
        ]

        def single_row():
            exif = self.get_exif_data(image_path)
            if exif:
                yield self.extract_key_info(exif, os.path.basename(image_path))
            else:
                empty = {f: '' for f in fieldnames}
                empty['Filename'] = os.path.basename(image_path)
                yield empty

        self._write_rows_to_csv(fieldnames, single_row(), output_csv, append=append)
        logger.info(f"Dati EXIF estratti e salvati in: {output_csv}")


# ---- CLI ----
def main():
    parser = argparse.ArgumentParser(description='Estrai info EXIF e organizza in CSV')
    parser.add_argument('input', help='File immagine o directory da processare')
    parser.add_argument('-o', '--output', default='exif_data.csv',
                        help='Nome del file CSV di output (default: exif_data.csv)')
    parser.add_argument('-a', '--append', action='store_true', help='Aggiungi al CSV esistente invece di sovrascrivere')
    parser.add_argument('-v', '--verbose', action='store_true', help='Output di debug')
    parser.add_argument('--formats', help='Formati accettati (separati da virgola), es: .jpg,.jpeg,.tif')
    args = parser.parse_args()

    # Configura logging qui (non a livello di import)
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')

    supported = None
    if args.formats:
        supported = tuple(s.strip().lower() for s in args.formats.split(','))

    extractor = ExifExtractor(supported_formats=supported)

    try:
        if os.path.isdir(args.input):
            extractor.process_directory(args.input, args.output, append=args.append)
        elif os.path.isfile(args.input):
            extractor.process_single_file(args.input, args.output, append=args.append)
        else:
            logger.error(f"Input non valido: {args.input}")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.warning("Interrotto dall'utente.")
        sys.exit(2)


if __name__ == "__main__":
    main()
