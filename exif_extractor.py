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
