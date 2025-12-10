"""
Organizzatore foto basato su EXIF:
crea cartelle in formato YYYY-MM/ISO e sposta i file.
"""
from pathlib import Path
from typing import List
import argparse
from PIL import Image
from PIL.ExifTags import TAGS
import shutil
