# Script che combina MarkItDown (per l’estrazione/parsificazione di documenti testuali) e Polars (per trasformazioni dati veloci) per processare una cartella di documenti d’ufficio: estrae tabelle dai PDF (con tabula-py / camelot come fallback), normalizza colonne e produce un CSV pulito unificato.

# doc-table-extractor

Mini-pipeline Python che estrae tabelle da PDF/DOCX/MD, normalizza con Polars e produce un CSV unificato.

## Requisiti
- Python 3.10+
- Java (per tabula)
- Ghostscript, OpenCV (per camelot)

## Installazione
```bash
python -m venv .venv
source .venv/bin/activate   # o .venv\Scripts\activate su Windows
pip install -r requirements.txt

## Esempio di test

Genera un PDF di esempio (contiene blocchi di testo, due tabelle e altro testo):
Output:

examples/test_multi_tables.pdf — PDF generato (input di esempio).
examples/out/ — CSV estratti da ogni metodo:
camelot_table_1.csv, camelot_table_2.csv, ...
tabula_table_1.csv, ...
pdfplumber_table_1.csv, ...
