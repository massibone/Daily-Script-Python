"""
Estrae le informazioni EXIF dalle immagini e le salva in formato CSV
"""

import os
import csv
import sys
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import argparse
from datetime import datetime
import logging

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ExifExtractor:
    def __init__(self):
        self.supported_formats = ('.jpg', '.jpeg', '.tiff', '.tif')
        
    def get_exif_data(self, image_path):
        """Estrae i dati EXIF da un'immagine"""
        try:
            with Image.open(image_path) as image:
                exif_data = image._getexif()
                if exif_data is None:
                    return {}
                
                exif_dict = {}
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    
                    # Gestione GPS info
                    if tag == 'GPSInfo':
                        gps_data = {}
                        for gps_tag_id, gps_value in value.items():
                            gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                            gps_data[gps_tag] = gps_value
                        exif_dict[tag] = gps_data
                    else:
                        exif_dict[tag] = value
                        
                return exif_dict
                            
        except Exception as e:
            logger.error(f"Errore nell'estrazione EXIF da {image_path}: {e}")
            return {}
        
    def convert_gps_to_decimal(self, gps_coord, gps_ref):
        """Converte le coordinate GPS in formato decimale"""
        try:
            if not gps_coord or not gps_ref:
                return None
                
            degrees = float(gps_coord[0])
            minutes = float(gps_coord[1])
            seconds = float(gps_coord[2])
            
            decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
            
            if gps_ref in ['S', 'W']:
                decimal = -decimal
                
            return round(decimal, 6)
        except:
            return None
    
    

    def extract_key_info(self, exif_data, filename):
        """Estrae le informazioni chiave dai dati EXIF"""
        info = {
            'Filename': filename,
            'DateTime': exif_data.get('DateTime', ''),
            'DateTimeOriginal': exif_data.get('DateTimeOriginal', ''),
            'Make': exif_data.get('Make', ''),
            'Model': exif_data.get('Model', ''),
            'ExposureTime': '',
            'FNumber': '',
            'ISO': exif_data.get('ISOSpeedRatings', ''),
            'FocalLength': '',
            'Flash': '',
            'WhiteBalance': exif_data.get('WhiteBalance', ''),
            'ImageWidth': exif_data.get('ExifImageWidth', ''),
            'ImageHeight': exif_data.get('ExifImageHeight', ''),
            'Orientation': exif_data.get('Orientation', ''),
            'GPS_Latitude': '',
            'GPS_Longitude': '',
            'GPS_Altitude': '',
            'Software': exif_data.get('Software', '')
        }
        
        # Gestione tempo di esposizione
        if 'ExposureTime' in exif_data:
            exp_time = exif_data['ExposureTime']
            if isinstance(exp_time, tuple):
                info['ExposureTime'] = f"{exp_time[0]}/{exp_time[1]}"
            else:
                info['ExposureTime'] = str(exp_time)
        
        # Gestione apertura
        if 'FNumber' in exif_data:
            f_num = exif_data['FNumber']
            if isinstance(f_num, tuple):
                info['FNumber'] = f"f/{f_num[0]/f_num[1]:.1f}"
            else:
                info['FNumber'] = f"f/{f_num}"
        
        # Gestione lunghezza focale
        if 'FocalLength' in exif_data:
            focal = exif_data['FocalLength']
            if isinstance(focal, tuple):
                info['FocalLength'] = f"{focal[0]/focal[1]:.1f}mm"
            else:
                info['FocalLength'] = f"{focal}mm"
        
        # Gestione flash
        if 'Flash' in exif_data:
            flash_value = exif_data['Flash']
            info['Flash'] = 'Yes' if flash_value & 1 else 'No'
        
        # Gestione GPS
        gps_info = exif_data.get('GPSInfo', {})
        if gps_info:
            lat_coord = gps_info.get('GPSLatitude')
            lat_ref = gps_info.get('GPSLatitudeRef')
            lon_coord = gps_info.get('GPSLongitude')
            lon_ref = gps_info.get('GPSLongitudeRef')
            alt_coord = gps_info.get('GPSAltitude')
            
            if lat_coord and lat_ref:
                info['GPS_Latitude'] = self.convert_gps_to_decimal(lat_coord, lat_ref)
            
            if lon_coord and lon_ref:
                info['GPS_Longitude'] = self.convert_gps_to_decimal(lon_coord, lon_ref)
                
            if alt_coord:
                if isinstance(alt_coord, tuple):
                    info['GPS_Altitude'] = f"{alt_coord[0]/alt_coord[1]:.2f}m"
                else:
                    info['GPS_Altitude'] = f"{alt_coord}m"
        
        return info
    
    def process_directory(self, directory_path, output_csv):
        """Processa tutte le immagini in una directory"""
        if not os.path.exists(directory_path):
            logger.error(f"Directory non trovata: {directory_path}")
            return
        
        image_files = []
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.lower().endswith(self.supported_formats):
                    image_files.append(os.path.join(root, file))
        
        if not image_files:
            logger.warning(f"Nessuna immagine trovata in: {directory_path}")
            return
        
        logger.info(f"Trovate {len(image_files)} immagini da processare")
        
        # Prepara il file CSV
        fieldnames = [
            'Filename', 'DateTime', 'DateTimeOriginal', 'Make', 'Model',
            'ExposureTime', 'FNumber', 'ISO', 'FocalLength', 'Flash',
            'WhiteBalance', 'ImageWidth', 'ImageHeight', 'Orientation',
            'GPS_Latitude', 'GPS_Longitude', 'GPS_Altitude', 'Software'
        ]
        
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for i, image_path in enumerate(image_files, 1):
                logger.info(f"Processando ({i}/{len(image_files)}): {os.path.basename(image_path)}")
                
                exif_data = self.get_exif_data(image_path)
                if exif_data:
                    key_info = self.extract_key_info(exif_data, os.path.basename(image_path))
                    writer.writerow(key_info)
                else:
                    # Scrivi una riga con solo il nome del file se non ci sono dati EXIF
                    empty_row = {field: '' for field in fieldnames}
                    empty_row['Filename'] = os.path.basename(image_path)
                    writer.writerow(empty_row)
        
        logger.info(f"Dati EXIF estratti e salvati in: {output_csv}")
    
    def process_single_file(self, image_path, output_csv):
        """Processa una singola immagine"""
        if not os.path.exists(image_path):
            logger.error(f"File non trovato: {image_path}")
            return
        
        if not image_path.lower().endswith(self.supported_formats):
            logger.error(f"Formato file non supportato: {image_path}")
            return
        
        exif_data = self.get_exif_data(image_path)
        
        fieldnames = [
            'Filename', 'DateTime', 'DateTimeOriginal', 'Make', 'Model',
            'ExposureTime', 'FNumber', 'ISO', 'FocalLength', 'Flash',
            'WhiteBalance', 'ImageWidth', 'ImageHeight', 'Orientation',
            'GPS_Latitude', 'GPS_Longitude', 'GPS_Altitude', 'Software'
        ]
        
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            if exif_data:
                key_info = self.extract_key_info(exif_data, os.path.basename(image_path))
                writer.writerow(key_info)
            else:
                empty_row = {field: '' for field in fieldnames}
                empty_row['Filename'] = os.path.basename(image_path)
                writer.writerow(empty_row)
        
        logger.info(f"Dati EXIF estratti e salvati in: {output_csv}")

def main():
    parser = argparse.ArgumentParser(description='Estrai info EXIF e organizza in CSV')
    parser.add_argument('input', help='File immagine o directory da processare')
    parser.add_argument('-o', '--output', default='exif_data.csv',
                       help='Nome del file CSV di output (default: exif_data.csv)')
    
    args = parser.parse_args()
    
    extractor = ExifExtractor()
    
    if os.path.isdir(args.input):
        extractor.process_directory(args.input, args.output)
    elif os.path.isfile(args.input):
        extractor.process_single_file(args.input, args.output)
    else:
        logger.error(f"Input non valido: {args.input}")
        sys.exit(1)

if __name__ == "__main__":
    main()

