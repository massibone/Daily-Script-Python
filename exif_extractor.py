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
    
