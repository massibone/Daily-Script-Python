# Estrazione automatica di testo da pdf multipli
import os
from pathlib import Path
from pdfminer.high_level import extract_text

def batch_extract_pdf_text(folder, output_folder=None):
"""
Estrae il testo da più file PDF in una cartella.

Args:
folder (str): Percorso della cartella contenente i file PDF.
output_folder (str, opzionale): Percorso della cartella di output per i file di testo estratti. Se non specificato, i file di testo saranno salvati nella stessa cartella dei file PDF.

Returns:
dict: Dizionario con i nomi dei file PDF come chiavi e il testo estratto come valori.
"""
# Verifica se la cartella esiste
if not os.path.exists(folder):
raise FileNotFoundError(f"La cartella '{folder}' non esiste.")

# Crea la cartella di output se non esiste
if output_folder and not os.path.exists(output_folder):
os.makedirs(output_folder)

# Inizializza il dizionario per memorizzare i risultati
results = {}

# Itera sui file PDF nella cartella
for file in Path(folder).glob('*.pdf'):
# Estrae il testo dal file PDF
text = extract_text(str(file))

# Salva il testo in un file di testo
if output_folder:
output_file = os.path.join(output_folder, file.stem + '.txt')
with open(output_file, 'w', encoding='utf-8') as f:
f.write(text)
else:
output_file = os.path.join(folder, file.stem + '.txt')
with open(output_file, 'w', encoding='utf-8') as f:
f.write(text)

# Aggiunge il risultato al dizionario
results[file.name] = text

return results

# Esempio di utilizzo
folder = '/path/to/pdf/files'
output_folder = '/path/to/output/folder'

results = batch_extract_pdf_text(folder, output_folder)

print(results)
