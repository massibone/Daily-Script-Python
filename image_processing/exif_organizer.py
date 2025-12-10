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

def organize_photos(src_dir: Path, dst_dir: Path) -> List[str]:
    """Crea cartelle YYYY-MM/ISO e sposta le foto."""
    dst_dir.mkdir(exist_ok=True)
    moved = []

    for img in src_dir.glob("*.jpg"):
        exif = extract_exif(img)

        # gestisce date mancanti
        folder_date = exif["date"][:7] if exif["date"] not in ("unknown", None) else "no_date"
        folder_iso = f"ISO{exif['iso']}" if exif["iso"] != "unknown" else "ISO_unknown"

        target = dst_dir / folder_date / folder_iso
        target.mkdir(parents=True, exist_ok=True)

        shutil.move(img, target / img.name)
        moved.append(str(img))

    return moved



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Organizzatore foto basato su EXIF")
    parser.add_argument("src", type=Path, help="Cartella sorgente")
    parser.add_argument("dst", type=Path, help="Cartella di destinazione")
    args = parser.parse_args()

    print(organize_photos(args.src, args.dst))

