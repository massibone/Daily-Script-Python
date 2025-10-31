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
