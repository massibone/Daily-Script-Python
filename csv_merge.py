'''
CSV Merge Tool - Unisce più file CSV in un unico file

Questo script permette di combinare più file CSV in un singolo file di output.
Supporta diverse modalità di unione e gestione degli header.

Funzionalità:
- Unione di multipli file CSV
- Gestione automatica degli header (skip duplicati)
- Validazione esistenza file
- Gestione errori con messaggi chiari
- Supporto encoding UTF-8
- Opzione per preservare o rimuovere header

Uso base:
    csv_merge(['file1.csv', 'file2.csv'], 'output.csv')

Uso avanzato con opzioni:
    csv_merge(['file1.csv', 'file2.csv'], 'output.csv', 
              keep_headers=True, skip_first_header=True)
'''

import csv
import os
import sys


def csv_merge(files, output, keep_headers=True, skip_first_header=True, encoding='utf-8'):
    """
    Unisce più file CSV in un unico file di output.
    
    Args:
        files (list): Lista di percorsi dei file CSV da unire
        output (str): Percorso del file CSV di output
        keep_headers (bool): Se True, mantiene l'header del primo file
        skip_first_header (bool): Se True, salta gli header dei file successivi al primo
        encoding (str): Encoding dei file (default: 'utf-8')
    
    Returns:
        bool: True se l'operazione è riuscita, False altrimenti
    
    Esempi:
        >>> csv_merge(['vendite_gen.csv', 'vendite_feb.csv'], 'vendite_totali.csv')
        >>> csv_merge(['dati1.csv', 'dati2.csv'], 'output.csv', keep_headers=False)
    """
    
    # Validazione input
    if not files:
        print("❌ Errore: Nessun file specificato")
        return False
    
    if not output:
        print("❌ Errore: Nome file output mancante")
        return False
    
    # Verifica esistenza file
    missing_files = [f for f in files if not os.path.exists(f)]
    if missing_files:
        print(f"❌ Errore: File non trovati: {', '.join(missing_files)}")
        return False
    
    try:
        total_rows = 0
        
        with open(output, 'w', newline='', encoding=encoding) as outcsv:
            writer = csv.writer(outcsv)
            
            for idx, f in enumerate(files):
                print(f"📄 Processando: {f}")
                
                with open(f, encoding=encoding) as incsv:
                    reader = csv.reader(incsv)
                    
                    for row_idx, row in enumerate(reader):
                        # Gestione header
                        if row_idx == 0:
                            if idx == 0 and keep_headers:
                                # Primo file: mantieni header se richiesto
                                writer.writerow(row)
                                total_rows += 1
                            elif idx > 0 and skip_first_header:
                                # File successivi: salta header se richiesto
                                continue
                        else:
                            writer.writerow(row)
                            total_rows += 1
        
        print(f"✅ Unione completata!")
        print(f"📊 {len(files)} file uniti → {total_rows} righe totali")
        print(f"💾 Output salvato in: {output}")
        return True
        
    except Exception as e:
        print(f"❌ Errore durante l'unione: {e}")
        return False


def csv_merge_cli():
    """Interfaccia da linea di comando per csv_merge"""
    if len(sys.argv) < 3:
        print("Uso: python csv_merge.py file1.csv file2.csv ... output.csv")
        print("\nEsempio:")
        print("  python csv_merge.py vendite_gen.csv vendite_feb.csv vendite_totali.csv")
        sys.exit(1)
    
    input_files = sys.argv[1:-1]
    output_file = sys.argv[-1]
    
    csv_merge(input_files, output_file)


if __name__ == '__main__':
    # Esempio d'uso quando eseguito direttamente
    # csv_merge(['a.csv', 'b.csv'], 'merged.csv')
    
    # Oppure usa la CLI
    csv_merge_cli()
```

---

## Dove posizionarlo nel README

Suggerisco di aggiungerlo in una nuova sezione `data_conversion/`:
```
Daily-Script-Python/
├── README.md
├── pdf_tools/
│   └── extract_text_from_pdf.py
├── data_conversion/
│   ├── json2csv.py
│   └── csv_merge.py          # ← NUOVO SCRIPT
├── image_processing/
│   ├── image_utils.py
│   ├── rename_photos.py
│   ├── rename_photos_by_date.py
│   ├── resize_image.py
│   ├── auto_crop.py
│   ├── create_thumbnail.py
│   └── exif_extractor.py
...
