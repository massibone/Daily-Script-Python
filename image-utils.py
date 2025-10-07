#image-utils.py

"""
Utility per la manipolazione di immagini con PIL/Pillow.
Versione ottimizzata con gestione errori, validazione e best practices.

Features:
- Ridimensionamento con mantenimento aspect ratio
- Rotazione senza perdita di contenuto
- Conversione formato con gestione trasparenza
- Logging completo
- Gestione errori robusta
- Validazione parametri

Autore: Versione Ottimizzata
Data: 2025
"""

import os
import logging
from pathlib import Path
from typing import Tuple, Optional, Union
from PIL import Image, ImageOps
from enum import Enum


# ============================================================================
# CONFIGURAZIONE LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


# ============================================================================
# ENUM E COSTANTI
# ============================================================================

class ResizeMode(Enum):
    """Modalità di ridimensionamento."""
    STRETCH = "stretch"           # Distorce per riempire
    FIT = "fit"                   # Mantiene aspect ratio, può avere bordi
    FILL = "fill"                 # Mantiene aspect ratio, ritaglia eccesso
    THUMBNAIL = "thumbnail"       # Mantiene aspect ratio, riduce solo


class ImageFormat(Enum):
    """Formati immagine supportati."""
    JPEG = "JPEG"
    JPG = "JPEG"
    PNG = "PNG"
    WEBP = "WEBP"
    BMP = "BMP"
    GIF = "GIF"
    TIFF = "TIFF"


# Qualità di default per i vari formati
DEFAULT_QUALITY = {
    "JPEG": 95,
    "WEBP": 90,
    "PNG": 9  # Livello di compressione 0-9
}


# ============================================================================
# ECCEZIONI PERSONALIZZATE
# ============================================================================

class ImageUtilsError(Exception):
    """Eccezione base per errori di image-utils."""
    pass


class InvalidImagePathError(ImageUtilsError):
    """Eccezione per percorsi immagine non validi."""
    pass


class InvalidParameterError(ImageUtilsError):
    """Eccezione per parametri non validi."""
    pass


# ============================================================================
# FUNZIONI DI VALIDAZIONE
# ============================================================================

def validate_image_path(image_path: Union[str, Path]) -> Path:
    """
    Valida che il percorso dell'immagine esista e sia leggibile.
    
    Args:
        image_path: Percorso dell'immagine
        
    Returns:
        Path: Oggetto Path validato
        
    Raises:
        InvalidImagePathError: Se il percorso non è valido
    """
    path = Path(image_path)
    
    if not path.exists():
        raise InvalidImagePathError(f"File non trovato: {path}")
    
    if not path.is_file():
        raise InvalidImagePathError(f"Il percorso non è un file: {path}")
    
    if not os.access(path, os.R_OK):
        raise InvalidImagePathError(f"File non leggibile: {path}")
    
    return path


def validate_output_path(output_path: Union[str, Path]) -> Path:
    """
    Valida che la directory di output esista o possa essere creata.
    
    Args:
        output_path: Percorso di output
        
    Returns:
        Path: Oggetto Path validato
        
    Raises:
        InvalidImagePathError: Se la directory non può essere creata
    """
    path = Path(output_path)
    
    # Crea la directory se non esiste
    path.parent.mkdir(parents=True, exist_ok=True)
    
    return path


def validate_size(size: Tuple[int, int]) -> Tuple[int, int]:
    """
    Valida che le dimensioni siano positive.
    
    Args:
        size: Tupla (larghezza, altezza)
        
    Returns:
        Tuple[int, int]: Dimensioni validate
        
    Raises:
        InvalidParameterError: Se le dimensioni non sono valide
    """
    if not isinstance(size, tuple) or len(size) != 2:
        raise InvalidParameterError(
            f"Size deve essere una tupla (larghezza, altezza), ricevuto: {size}"
        )
    
    width, height = size
    
    if not isinstance(width, int) or not isinstance(height, int):
        raise InvalidParameterError(
            f"Larghezza e altezza devono essere interi, ricevuto: {size}"
        )
    
    if width <= 0 or height <= 0:
        raise InvalidParameterError(
            f"Dimensioni devono essere positive, ricevuto: {size}"
        )
    
    return size


# ============================================================================
# FUNZIONI PRINCIPALI OTTIMIZZATE
# ============================================================================

def resize_image(
    image_path: Union[str, Path],
    output_path: Union[str, Path],
    size: Tuple[int, int],
    mode: ResizeMode = ResizeMode.FIT,
    quality: Optional[int] = None,
    resample: Image.Resampling = Image.Resampling.LANCZOS
) -> None:
    """
    Ridimensiona un'immagine con varie modalità e mantenimento qualità.
    
    Args:
        image_path: Percorso dell'immagine di input
        output_path: Percorso dell'immagine di output
        size: Dimensioni target (larghezza, altezza)
        mode: Modalità di ridimensionamento (default: FIT)
        quality: Qualità output (1-100 per JPEG, 1-9 per PNG)
        resample: Algoritmo di resampling (default: LANCZOS)
        
    Raises:
        InvalidImagePathError: Se i percorsi non sono validi
        InvalidParameterError: Se i parametri non sono validi
        ImageUtilsError: Per altri errori durante il processing
        
    Example:
        >>> resize_image("input.jpg", "output.jpg", (800, 600), ResizeMode.FIT)
    """
    try:
        # Validazione
        image_path = validate_image_path(image_path)
        output_path = validate_output_path(output_path)
        size = validate_size(size)
        
        logger.info(f"Ridimensionamento {image_path} -> {output_path} ({size}, mode={mode.value})")
        
        # Apri immagine
        with Image.open(image_path) as img:
            # Salva formato originale
            original_format = img.format
            
            # Applica ridimensionamento in base alla modalità
            if mode == ResizeMode.STRETCH:
                # Distorce per riempire esattamente le dimensioni
                resized = img.resize(size, resample)
                
            elif mode == ResizeMode.FIT:
                # Mantiene aspect ratio, aggiunge bordi se necessario
                resized = ImageOps.pad(img, size, resample, color=(255, 255, 255))
                
            elif mode == ResizeMode.FILL:
                # Mantiene aspect ratio, ritaglia l'eccesso
                resized = ImageOps.fit(img, size, resample)
                
            elif mode == ResizeMode.THUMBNAIL:
                # Riduce mantenendo aspect ratio (non ingrandisce)
                img.thumbnail(size, resample)
                resized = img
            
            else:
                raise InvalidParameterError(f"Modalità non valida: {mode}")
            
            # Determina qualità
            if quality is None:
                quality = DEFAULT_QUALITY.get(original_format, 95)
            
            # Salva con parametri ottimizzati
            save_kwargs = _get_save_kwargs(output_path, quality)
            resized.save(output_path, **save_kwargs)
            
        logger.info(f"✅ Ridimensionamento completato: {output_path}")
        
    except (InvalidImagePathError, InvalidParameterError):
        raise
    except Exception as e:
        logger.error(f"❌ Errore durante il ridimensionamento: {e}")
        raise ImageUtilsError(f"Errore ridimensionamento: {e}") from e


def rotate_image(
    image_path: Union[str, Path],
    output_path: Union[str, Path],
    angle: float,
    expand: bool = True,
    fill_color: Tuple[int, int, int] = (255, 255, 255),
    quality: Optional[int] = None
) -> None:
    """
    Ruota un'immagine con gestione corretta dell'espansione.
    
    Args:
        image_path: Percorso dell'immagine di input
        output_path: Percorso dell'immagine di output
        angle: Angolo di rotazione in gradi (senso antiorario)
        expand: Se True, espande l'immagine per evitare ritagli
        fill_color: Colore di riempimento RGB per gli angoli
        quality: Qualità output
        
    Raises:
        InvalidImagePathError: Se i percorsi non sono validi
        ImageUtilsError: Per altri errori durante il processing
        
    Example:
        >>> rotate_image("input.jpg", "output.jpg", 45, expand=True)
    """
    try:
        # Validazione
        image_path = validate_image_path(image_path)
        output_path = validate_output_path(output_path)
        
        # Normalizza angolo tra 0 e 360
        angle = angle % 360
        
        logger.info(f"Rotazione {image_path} -> {output_path} ({angle}°, expand={expand})")
        
        with Image.open(image_path) as img:
            original_format = img.format
            
            # Gestione trasparenza
            has_transparency = img.mode in ('RGBA', 'LA', 'P')
            
            if has_transparency and fill_color:
                # Per immagini trasparenti, usa colore trasparente
                fill_color = fill_color + (0,)  # Aggiungi canale alpha
            
            # Ruota con espansione
            rotated = img.rotate(
                angle,
                expand=expand,
                fillcolor=fill_color,
                resample=Image.Resampling.BICUBIC
            )
            
            # Determina qualità
            if quality is None:
                quality = DEFAULT_QUALITY.get(original_format, 95)
            
            # Salva
            save_kwargs = _get_save_kwargs(output_path, quality)
            rotated.save(output_path, **save_kwargs)
            
        logger.info(f"✅ Rotazione completata: {output_path}")
        
    except InvalidImagePathError:
        raise
    except Exception as e:
        logger.error(f"❌ Errore durante la rotazione: {e}")
        raise ImageUtilsError(f"Errore rotazione: {e}") from e


def convert_image_format(
    image_path: Union[str, Path],
    output_path: Union[str, Path],
    output_format: Optional[str] = None,
    quality: Optional[int] = None,
    optimize: bool = True
) -> None:
    """
    Converte il formato di un'immagine con gestione trasparenza.
    
    Args:
        image_path: Percorso dell'immagine di input
        output_path: Percorso dell'immagine di output
        output_format: Formato di output (se None, dedotto da estensione)
        quality: Qualità output
        optimize: Se True, ottimizza la compressione
        
    Raises:
        InvalidImagePathError: Se i percorsi non sono validi
        InvalidParameterError: Se il formato non è supportato
        ImageUtilsError: Per altri errori durante il processing
        
    Example:
        >>> convert_image_format("input.png", "output.jpg", quality=95)
    """
    try:
        # Validazione
        image_path = validate_image_path(image_path)
        output_path = validate_output_path(output_path)
        
        # Determina formato output
        if output_format is None:
            ext = output_path.suffix.upper().lstrip('.')
            try:
                output_format = ImageFormat[ext].value
            except KeyError:
                raise InvalidParameterError(f"Formato non supportato: {ext}")
        else:
            output_format = output_format.upper()
        
        logger.info(f"Conversione {image_path} -> {output_path} (formato={output_format})")
        
        with Image.open(image_path) as img:
            # Gestione trasparenza per JPEG
            if output_format == "JPEG" and img.mode in ('RGBA', 'LA', 'P'):
                logger.warning("Conversione RGBA -> JPEG: rimozione trasparenza")
                # Crea sfondo bianco
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img
            
            # Converti modalità se necessario
            if output_format == "JPEG" and img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')
            
            # Determina qualità
            if quality is None:
                quality = DEFAULT_QUALITY.get(output_format, 95)
            
            # Salva con formato specificato
            save_kwargs = _get_save_kwargs(output_path, quality, output_format)
            save_kwargs['optimize'] = optimize
            
            img.save(output_path, format=output_format, **save_kwargs)
            
        logger.info(f"✅ Conversione completata: {output_path}")
        
    except (InvalidImagePathError, InvalidParameterError):
        raise
    except Exception as e:
        logger.error(f"❌ Errore durante la conversione: {e}")
        raise ImageUtilsError(f"Errore conversione: {e}") from e


# ============================================================================
# FUNZIONI UTILITY
# ============================================================================

def _get_save_kwargs(output_path: Path, quality: int, 
                     format_override: Optional[str] = None) -> dict:
    """
    Ottiene i parametri ottimali per il salvataggio in base al formato.
    
    Args:
        output_path: Percorso di output
        quality: Qualità desiderata
        format_override: Formato da usare invece dell'estensione
        
    Returns:
        dict: Parametri per Image.save()
    """
    if format_override:
        format_str = format_override
    else:
        ext = output_path.suffix.upper().lstrip('.')
        format_str = ImageFormat[ext].value if ext in ImageFormat.__members__ else ext
    
    kwargs = {}
    
    if format_str == "JPEG":
        kwargs['quality'] = quality
        kwargs['optimize'] = True
        kwargs['progressive'] = True
    elif format_str == "PNG":
        kwargs['compress_level'] = min(9, max(0, quality // 10))
        kwargs['optimize'] = True
    elif format_str == "WEBP":
        kwargs['quality'] = quality
        kwargs['method'] = 6  # Migliore compressione
    
    return kwargs


def get_image_info(image_path: Union[str, Path]) -> dict:
    """
    Ottiene informazioni su un'immagine.
    
    Args:
        image_path: Percorso dell'immagine
        
    Returns:
        dict: Informazioni sull'immagine
        
    Example:
        >>> info = get_image_info("image.jpg")
        >>> print(info['size'], info['format'])
    """
    image_path = validate_image_path(image_path)
    
    with Image.open(image_path) as img:
        return {
            'path': str(image_path),
            'format': img.format,
            'mode': img.mode,
            'size': img.size,
            'width': img.width,
            'height': img.height,
            'aspect_ratio': img.width / img.height,
        }


# ============================================================================
# FUNZIONE BATCH
# ============================================================================

def batch_process_images(
    input_dir: Union[str, Path],
    output_dir: Union[str, Path],
    operation: str,
    **kwargs
) -> None:
    """
    Elabora in batch tutte le immagini in una directory.
    
    Args:
        input_dir: Directory di input
        output_dir: Directory di output
        operation: Operazione da eseguire ('resize', 'rotate', 'convert')
        **kwargs: Parametri per l'operazione specifica
        
    Example:
        >>> batch_process_images(
        ...     "input/", "output/",
        ...     "resize", size=(800, 600), mode=ResizeMode.FIT
        ... )
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Estensioni supportate
    extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.tiff'}
    
    # Trova tutte le immagini
    images = [f for f in input_path.iterdir() 
              if f.is_file() and f.suffix.lower() in extensions]
    
    logger.info(f"Trovate {len(images)} immagini da processare")
    
    operations = {
        'resize': resize_image,
        'rotate': rotate_image,
        'convert': convert_image_format
    }
    
    if operation not in operations:
        raise InvalidParameterError(f"Operazione non valida: {operation}")
    
    func = operations[operation]
    success = 0
    errors = 0
    
    for img_path in images:
        try:
            output_file = output_path / img_path.name
            func(img_path, output_file, **kwargs)
            success += 1
        except Exception as e:
            logger.error(f"Errore processing {img_path.name}: {e}")
            errors += 1
    
    logger.info(f"✅ Completato: {success} successi, {errors} errori")


# ============================================================================
# FUNZIONE MAIN - ESEMPI D'USO
# ============================================================================

def main():
    """
    Funzione principale con esempi d'uso corretti.
    """
    logger.info("="*70)
    logger.info("🖼️  IMAGE UTILS - Esempi d'Uso")
    logger.info("="*70)
    
    # Percorsi di esempio (modifica secondo necessità)
    input_image = "input.jpg"
    
    # Verifica se il file esiste
    if not Path(input_image).exists():
        logger.warning(f"⚠️  File {input_image} non trovato. Creazione esempio...")
        # Crea un'immagine di test
        test_img = Image.new('RGB', (1200, 800), color=(100, 150, 200))
        test_img.save(input_image, quality=95)
        logger.info(f"✅ Creata immagine di test: {input_image}")
    
    try:
        # Esempio 1: Ridimensionamento (mantiene aspect ratio)
        logger.info("\n📋 Esempio 1: Ridimensionamento con FIT")
        resize_image(
            input_image,
            "output_resized_fit.jpg",
            (800, 600),
            mode=ResizeMode.FIT
        )
        
        # Esempio 2: Ridimensionamento FILL (ritaglia)
        logger.info("\n📋 Esempio 2: Ridimensionamento con FILL")
        resize_image(
            input_image,
            "output_resized_fill.jpg",
            (800, 600),
            mode=ResizeMode.FILL
        )
        
        # Esempio 3: Rotazione con espansione
        logger.info("\n📋 Esempio 3: Rotazione 45°")
        rotate_image(
            input_image,
            "output_rotated.jpg",
            45,
            expand=True
        )
        
        # Esempio 4: Conversione formato
        logger.info("\n📋 Esempio 4: Conversione JPG -> PNG")
        convert_image_format(
            input_image,
            "output_converted.png",
            quality=90
        )
        
        # Esempio 5: Info immagine
        logger.info("\n📋 Esempio 5: Informazioni Immagine")
        info = get_image_info(input_image)
        for key, value in info.items():
            logger.info(f"  {key}: {value}")
        
        logger.info("\n" + "="*70)
        logger.info("✅ Tutti gli esempi completati con successo!")
        logger.info("="*70)
        
    except ImageUtilsError as e:
        logger.error(f"❌ Errore: {e}")
    except Exception as e:
        logger.error(f"❌ Errore imprevisto: {e}", exc_info=True)


if __name__ == "__main__":
    main()
