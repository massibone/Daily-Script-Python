
"""
Script per rinominare foto in base alla data di scatto o modifica.

Features:
- Estrazione data da metadati EXIF
- Fallback su data modifica file
- Pattern di naming personalizzabili
- Gestione duplicati automatica
- Preview prima della rinomina
- Backup automatico
- Supporto batch processing
- Organizzazione per cartelle (anno/mese)
- Logging completo

Formati supportati:
- JPG/JPEG
- PNG
- HEIC/HEIF
- RAW (CR2, NEF, ARW, DNG, ecc.)
- TIFF
- BMP
- WEBP

Pattern disponibili:
- {year} - Anno (4 cifre)
- {month} - Mese (2 cifre)
- {day} - Giorno (2 cifre)
- {hour} - Ora (2 cifre)
- {minute} - Minuti (2 cifre)
- {second} - Secondi (2 cifre)
- {counter} - Contatore incrementale
- {original} - Nome originale

Esempi:
    python rename_photos_by_date.py /path/to/photos
    python rename_photos_by_date.py /path/to/photos --pattern "{year}{month}{day}_{hour}{minute}{second}"
    python rename_photos_by_date.py /path/to/photos --organize-by-date --preview

Autore: Photo Organizer System
Data: 2025
"""

import os
import sys
import shutil
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
from datetime import datetime
from collections import defaultdict

from PIL import Image
from PIL.ExifTags import TAGS


# ============================================================================
# CONFIGURAZIONE LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURAZIONE GLOBALE
# ============================================================================

# Estensioni supportate
IMAGE_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.heic', '.heif',
    '.cr2', '.nef', '.arw', '.dng', '.orf', '.rw2',
    '.tiff', '.tif', '.bmp', '.webp', '.gif'
}

# Pattern di default
DEFAULT_PATTERN = "{year}{month}{day}_{hour}{minute}{second}"

# Tag EXIF per data scatto
EXIF_DATE_TAGS = [
    'DateTimeOriginal',      # Data scatto originale
    'DateTimeDigitized',     # Data digitalizzazione
    'DateTime',              # Data modifica
]


# ============================================================================
# CLASSE PRINCIPALE: PhotoRenamer
# ============================================================================

class PhotoRenamer:
    """
    Rinomina foto in base alla data di scatto o modifica.
    
    Attributes:
        directory: Path della directory da processare
        pattern: Pattern per il nuovo nome
        organize_by_date: Se organizzare in sottocartelle anno/mese
        backup: Se creare backup
        dry_run: Se True, solo preview senza rinominare
    """
    
    def __init__(
        self,
        directory: Union[str, Path],
        pattern: str = DEFAULT_PATTERN,
        organize_by_date: bool = False,
        backup: bool = True,
        dry_run: bool = False,
        recursive: bool = False
    ):
        """
        Inizializza il rinominatore.
        
        Args:
            directory: Directory con le foto
            pattern: Pattern per il nome (es: "{year}{month}{day}_{counter}")
            organize_by_date: Se True, organizza in cartelle anno/mese
            backup: Se True, crea backup prima di rinominare
            dry_run: Se True, mostra solo preview
            recursive: Se True, processa anche sottocartelle
        """
        self.directory = Path(directory)
        self.pattern = pattern
        self.organize_by_date = organize_by_date
        self.backup = backup
        self.dry_run = dry_run
        self.recursive = recursive
        
        self.backup_dir = None
        self.stats = {
            'total': 0,
            'renamed': 0,
            'skipped': 0,
            'errors': 0
        }
        
        # Validazione
        if not self.directory.exists():
            raise FileNotFoundError(f"Directory non trovata: {self.directory}")
        
        if not self.directory.is_dir():
            raise NotADirectoryError(f"Non è una directory: {self.directory}")
        
        logger.info(f"Inizializzato rinominatore per: {self.directory}")
        logger.info(f"Pattern: {self.pattern}")
        logger.info(f"Modalità: {'PREVIEW' if self.dry_run else 'ESECUZIONE'}")
    
    
    def run(self) -> Dict[str, int]:
        """
        Esegue la rinominazione delle foto.
        
        Returns:
            Dizionario con statistiche
        """
        logger.info("="*70)
        logger.info("INIZIO PROCESSO DI RINOMINAZIONE")
        logger.info("="*70)
        
        # 1. Trova tutte le foto
        photos = self._find_photos()
        self.stats['total'] = len(photos)
        
        if len(photos) == 0:
            logger.warning("⚠️  Nessuna foto trovata!")
            return self.stats
        
        logger.info(f"📸 Trovate {len(photos)} foto")
        
        # 2. Backup
        if self.backup and not self.dry_run:
            self._create_backup(photos)
        
        # 3. Analizza e prepara rinominazioni
        rename_plan = self._prepare_rename_plan(photos)
        
        # 4. Preview o esecuzione
        if self.dry_run:
            self._show_preview(rename_plan)
        else:
            self._execute_rename(rename_plan)
        
        # 5. Statistiche finali
        self._show_statistics()
        
        logger.info("="*70)
        logger.info("PROCESSO COMPLETATO")
        logger.info("="*70)
        
        return self.stats
    
    
    def _find_photos(self) -> List[Path]:
        """
        Trova tutte le foto nella directory.
        
        Returns:
            Lista di Path delle foto
        """
        logger.info("🔍 Ricerca foto in corso...")
        
        photos = []
        
        if self.recursive:
            # Ricerca ricorsiva
            for ext in IMAGE_EXTENSIONS:
                photos.extend(self.directory.rglob(f"*{ext}"))
                photos.extend(self.directory.rglob(f"*{ext.upper()}"))
        else:
            # Solo directory corrente
            for ext in IMAGE_EXTENSIONS:
                photos.extend(self.directory.glob(f"*{ext}"))
                photos.extend(self.directory.glob(f"*{ext.upper()}"))
        
        # Ordina per data modifica
        photos.sort(key=lambda p: p.stat().st_mtime)
        
        return photos
    
    
    def _create_backup(self, photos: List[Path]) -> None:
        """
        Crea backup delle foto originali.
        
        Args:
            photos: Lista foto da backuppare
        """
        logger.info("💾 Creazione backup...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = self.directory / f"backup_{timestamp}"
        self.backup_dir.mkdir(exist_ok=True)
        
        for photo in photos:
            try:
                # Mantieni struttura sottocartelle relative
                rel_path = photo.relative_to(self.directory)
                backup_path = self.backup_dir / rel_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                
                shutil.copy2(photo, backup_path)
            except Exception as e:
                logger.error(f"Errore backup {photo.name}: {e}")
        
        logger.info(f"✅ Backup creato: {self.backup_dir}")
    
    
    def _prepare_rename_plan(self, photos: List[Path]) -> List[Dict]:
        """
        Prepara il piano di rinominazione.
        
        Args:
            photos: Lista foto da analizzare
            
        Returns:
            Lista di dizionari con info rinominazione
        """
        logger.info("📋 Preparazione piano di rinominazione...")
        
        rename_plan = []
        counter_by_date = defaultdict(int)
        
        for photo in photos:
            try:
                # Estrai data
                date = self._get_photo_date(photo)
                
                if date is None:
                    logger.warning(f"⚠️  Data non trovata: {photo.name}, uso data file")
                    date = datetime.fromtimestamp(photo.stat().st_mtime)
                
                # Incrementa contatore per questa data
                date_key = date.strftime("%Y%m%d")
                counter_by_date[date_key] += 1
                counter = counter_by_date[date_key]
                
                # Genera nuovo nome
                new_name = self._generate_new_name(photo, date, counter)
                
                # Determina path destinazione
                if self.organize_by_date:
                    dest_dir = self.directory / str(date.year) / f"{date.month:02d}"
                    dest_dir.mkdir(parents=True, exist_ok=True)
                else:
                    dest_dir = photo.parent
                
                new_path = dest_dir / new_name
                
                # Gestisci duplicati
                new_path = self._handle_duplicate(new_path)
                
                rename_plan.append({
                    'original': photo,
                    'new_path': new_path,
                    'date': date,
                    'counter': counter
                })
                
            except Exception as e:
                logger.error(f"❌ Errore analisi {photo.name}: {e}")
                self.stats['errors'] += 1
        
        return rename_plan
    
    
    def _get_photo_date(self, photo_path: Path) -> Optional[datetime]:
        """
        Estrae data di scatto dai metadati EXIF.
        
        Args:
            photo_path: Path della foto
            
        Returns:
            datetime o None se non trovato
        """
        try:
            with Image.open(photo_path) as img:
                # Estrai EXIF
                exif = img._getexif()
                
                if exif is None:
                    return None
                
                # Cerca tag data
                for tag_id, value in exif.items():
                    tag_name = TAGS.get(tag_id, tag_id)
                    
                    if tag_name in EXIF_DATE_TAGS:
                        # Parse data formato EXIF: "YYYY:MM:DD HH:MM:SS"
                        try:
                            return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                        except ValueError:
                            continue
                
        except Exception as e:
            logger.debug(f"Impossibile leggere EXIF da {photo_path.name}: {e}")
        
        return None
    
    
    def _generate_new_name(
        self,
        photo: Path,
        date: datetime,
        counter: int
    ) -> str:
        """
        Genera nuovo nome basato sul pattern.
        
        Args:
            photo: Path foto originale
            date: Data di scatto
            counter: Contatore per duplicati
            
        Returns:
            Nuovo nome file
        """
        # Mappa variabili
        variables = {
            'year': date.strftime('%Y'),
            'month': date.strftime('%m'),
            'day': date.strftime('%d'),
            'hour': date.strftime('%H'),
            'minute': date.strftime('%M'),
            'second': date.strftime('%S'),
            'counter': f"{counter:03d}",
            'original': photo.stem
        }
        
        # Sostituisci variabili nel pattern
        new_name = self.pattern
        for key, value in variables.items():
            new_name = new_name.replace(f"{{{key}}}", value)
        
        # Aggiungi estensione originale
        new_name += photo.suffix.lower()
        
        return new_name
    
    
    def _handle_duplicate(self, path: Path) -> Path:
        """
        Gestisce nomi duplicati aggiungendo suffisso.
        
        Args:
            path: Path da verificare
            
        Returns:
            Path univoco
        """
        if not path.exists():
            return path
        
        # Aggiungi suffisso numerico
        stem = path.stem
        ext = path.suffix
        counter = 1
        
        while True:
            new_path = path.parent / f"{stem}_{counter:02d}{ext}"
            if not new_path.exists():
                return new_path
            counter += 1
    
    
    def _show_preview(self, rename_plan: List[Dict]) -> None:
        """
        Mostra preview delle rinominazioni.
        
        Args:
            rename_plan: Piano di rinominazione
        """
        logger.info("\n" + "="*70)
        logger.info("PREVIEW RINOMINAZIONI")
        logger.info("="*70 + "\n")
        
        for i, item in enumerate(rename_plan, 1):
            original = item['original']
            new_path = item['new_path']
            date = item['date']
            
            logger.info(f"{i}. {original.name}")
            logger.info(f"   → {new_path.name}")
            logger.info(f"   📅 Data: {date.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if self.organize_by_date:
                logger.info(f"   📁 Cartella: {new_path.parent.relative_to(self.directory)}")
            
            logger.info("")
    
    
    def _execute_rename(self, rename_plan: List[Dict]) -> None:
        """
        Esegue le rinominazioni.
        
        Args:
            rename_plan: Piano di rinominazione
        """
        logger.info("🚀 Esecuzione rinominazioni...")
        
        for item in rename_plan:
            original = item['original']
            new_path = item['new_path']
            
            try:
                # Crea directory se necessaria
                new_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Rinomina/sposta file
                original.rename(new_path)
                
                logger.info(f"✅ {original.name} → {new_path.name}")
                self.stats['renamed'] += 1
                
            except Exception as e:
                logger.error(f"❌ Errore rinomina {original.name}: {e}")
                self.stats['errors'] += 1
    
    
    def _show_statistics(self) -> None:
        """Mostra statistiche finali."""
        logger.info("\n" + "="*70)
        logger.info("STATISTICHE")
        logger.info("="*70)
        logger.info(f"📊 Totale foto: {self.stats['total']}")
        logger.info(f"✅ Rinominate: {self.stats['renamed']}")
        logger.info(f"⚠️  Saltate: {self.stats['skipped']}")
        logger.info(f"❌ Errori: {self.stats['errors']}")
        
        if self.backup_dir:
            logger.info(f"\n💾 Backup salvato in: {self.backup_dir}")


# ============================================================================
# FUNZIONI UTILITY
# ============================================================================

def validate_pattern(pattern: str) -> bool:
    """
    Valida il pattern di naming.
    
    Args:
        pattern: Pattern da validare
        
    Returns:
        True se valido
    """
    valid_vars = {
        'year', 'month', 'day', 'hour', 
        'minute', 'second', 'counter', 'original'
    }
    
    # Trova tutte le variabili nel pattern
    import re
    found_vars = set(re.findall(r'\{(\w+)\}', pattern))
    
    # Verifica che siano tutte valide
    invalid_vars = found_vars - valid_vars
    
    if invalid_vars:
        logger.error(f"❌ Variabili non valide nel pattern: {invalid_vars}")
        logger.info(f"Variabili disponibili: {valid_vars}")
        return False
    
    return True


def show_pattern_examples() -> None:
    """Mostra esempi di pattern."""
    examples = [
        ("{year}{month}{day}_{hour}{minute}{second}", "20250123_143052.jpg"),
        ("{year}-{month}-{day}_{counter}", "2025-01-23_001.jpg"),
        ("IMG_{year}{month}{day}_{counter}", "IMG_20250123_001.jpg"),
        ("{year}/{month}/{day}_{hour}{minute}", "2025/01/23_1430.jpg"),
        ("{original}_{year}{month}{day}", "vacation_20250123.jpg"),
    ]
    
    print("\n" + "="*70)
    print("ESEMPI DI PATTERN")
    print("="*70)
    
    for pattern, example in examples:
        print(f"\nPattern: {pattern}")
        print(f"Risultato: {example}")
    
    print("\n" + "="*70)
    print("VARIABILI DISPONIBILI")
    print("="*70)
    print("{year}    - Anno (4 cifre, es: 2025)")
    print("{month}   - Mese (2 cifre, es: 01)")
    print("{day}     - Giorno (2 cifre, es: 23)")
    print("{hour}    - Ora (2 cifre, es: 14)")
    print("{minute}  - Minuti (2 cifre, es: 30)")
    print("{second}  - Secondi (2 cifre, es: 52)")
    print("{counter} - Contatore (3 cifre, es: 001)")
    print("{original}- Nome originale (senza estensione)")
    print("="*70 + "\n")


# ============================================================================
# CLI - INTERFACCIA A LINEA DI COMANDO
# ============================================================================

def main():
    """Funzione principale CLI."""
    parser = argparse.ArgumentParser(
        description="Rinomina foto in base alla data di scatto",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi d'uso:
  %(prog)s /path/to/photos
  %(prog)s /path/to/photos --pattern "{year}{month}{day}_{counter}"
  %(prog)s /path/to/photos --organize-by-date
  %(prog)s /path/to/photos --preview
  %(prog)s /path/to/photos --recursive --no-backup
  
Per vedere esempi di pattern:
  %(prog)s --examples
        """
    )
    
    parser.add_argument(
        'directory',
        nargs='?',
        help='Directory contenente le foto'
    )
    
    parser.add_argument(
        '-p', '--pattern',
        default=DEFAULT_PATTERN,
        help=f'Pattern per il nuovo nome (default: {DEFAULT_PATTERN})'
    )
    
    parser.add_argument(
        '-o', '--organize-by-date',
        action='store_true',
        help='Organizza foto in cartelle anno/mese'
    )
    
    parser.add_argument(
        '--preview',
        action='store_true',
        help='Mostra solo preview senza rinominare'
    )
    
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Processa anche le sottocartelle'
    )
    
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Non creare backup'
    )
    
    parser.add_argument(
        '--examples',
        action='store_true',
        help='Mostra esempi di pattern'
    )
    
    args = parser.parse_args()
    
    # Mostra esempi
    if args.examples:
        show_pattern_examples()
        return 0
    
    # Verifica directory
    if not args.directory:
        parser.print_help()
        return 1
    
    # Valida pattern
    if not validate_pattern(args.pattern):
        return 1
    
    try:
        # Crea rinominatore
        renamer = PhotoRenamer(
            directory=args.directory,
            pattern=args.pattern,
            organize_by_date=args.organize_by_date,
            backup=not args.no_backup,
            dry_run=args.preview,
            recursive=args.recursive
        )
        
        # Esegui
        stats = renamer.run()
        
        # Exit code
        if stats['errors'] > 0:
            return 1
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Errore: {e}")
        return 1


# ============================================================================
# ESEMPIO D'USO PROGRAMMATICO
# ============================================================================

def example_usage():
    """Esempio di utilizzo come modulo Python."""
    
    # Esempio 1: Rinominazione semplice
    renamer = PhotoRenamer(
        directory="/path/to/photos",
        pattern="{year}{month}{day}_{hour}{minute}{second}",
        backup=True,
        dry_run=False  # True per preview
    )
    stats = renamer.run()
    
    # Esempio 2: Organizzazione per data
    renamer = PhotoRenamer(
        directory="/path/to/photos",
        pattern="{year}-{month}-{day}_{counter}",
        organize_by_date=True,
        recursive=True
    )
    stats = renamer.run()
    
    print(f"Rinominate: {stats['renamed']} foto")


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    sys.exit(main())

