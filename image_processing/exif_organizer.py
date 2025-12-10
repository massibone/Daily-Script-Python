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

def extract_exif(image_path: Path) -> dict[str, str]:
    """Estrae data e ISO da EXIF della foto."""
    try:
        with Image.open(image_path) as img:
            exif = img.getexif()

            date = exif.get(306, "unknown")       # DateTime
            iso = exif.get(34855, "unknown")      # ISOSpeedRatings

            return {
                "date": str(date),
                "iso": str(iso)
            }
    except Exception:
        return {"date": "unknown", "iso": "unknown"}
