
# Estrazione automatica di testo da pdf multipli
import os
from pathlib import Path
from pdfminer.high_level import extract_text
import logging

# Configurazione logging per debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def batch_extract_pdf_text(folder, output_folder=None):
    """
    Estrae il testo da più file PDF in una cartella.
    
    Args:
        folder (str): Percorso della cartella contenente i file PDF.
        output_folder (str, opzionale): Percorso della cartella di output per i file di testo.
            Se non specificato, i file di testo saranno salvati nella stessa cartella dei PDF.
    
    Returns:
        dict: Dizionario con i nomi dei file PDF come chiavi e il testo estratto come valori.
        
    Raises:
        FileNotFoundError: Se la cartella specificata non esiste.
        NotADirectoryError: Se il percorso non è una directory.
    """
    # Conversione a Path per gestione più moderna dei percorsi
    folder_path = Path(folder)
    
    # Validazione input
    if not folder_path.exists():
        raise FileNotFoundError(f"La cartella '{folder}' non esiste.")
    
    if not folder_path.is_dir():
        raise NotADirectoryError(f"'{folder}' non è una directory.")
    
    # Crea la cartella di output se specificata
    if output_folder:
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = folder_path
    
    # Inizializza il dizionario per i risultati
    results = {}
    errors = {}
    
    # Itera sui file PDF
    pdf_files = list(folder_path.glob('*.pdf'))
    
    if not pdf_files:
        logger.warning(f"Nessun file PDF trovato nella cartella '{folder}'")
        return results
    
    logger.info(f"Trovati {len(pdf_files)} file PDF da processare")
    
    for pdf_file in pdf_files:
        try:
            # Estrae il testo dal PDF
            logger.info(f"Elaborazione di: {pdf_file.name}")
            text = extract_text(str(pdf_file))
            
            # Salva il testo in un file
            output_file = output_path / f"{pdf_file.stem}.txt"
            output_file.write_text(text, encoding='utf-8')
            
            # Memorizza il risultato
            results[pdf_file.name] = text
            logger.info(f"✓ Completato: {pdf_file.name}")
            
        except Exception as e:
            # Gestisce errori senza interrompere l'elaborazione
            error_msg = f"Errore nell'elaborazione di {pdf_file.name}: {str(e)}"
            logger.error(error_msg)
            errors[pdf_file.name] = str(e)
    
    # Report finale
    logger.info(f"\n{'='*50}")
    logger.info(f"Elaborazione completata:")
    logger.info(f"  - File processati con successo: {len(results)}")
    logger.info(f"  - File con errori: {len(errors)}")
    
    if errors:
        logger.warning(f"\nErrori riscontrati:")
        for file, error in errors.items():
            logger.warning(f"  - {file}: {error}")
    
    return results

# Esempio di utilizzo migliorato
if __name__ == "__main__":
    # Usa percorsi relativi o esistenti
    folder = './pdf_files'  # Cartella nella directory corrente
    output_folder = './output_texts'  # Opzionale
    
    try:
        results = batch_extract_pdf_text(folder, output_folder)
        
        # Mostra statistiche invece di tutto il contenuto
        print(f"\nRisultati dell'estrazione:")
        for filename, text in results.items():
            print(f"  - {filename}: {len(text)} caratteri estratti")
            
    except (FileNotFoundError, NotADirectoryError) as e:
        print(f"Errore: {e}")

